import re
from typing import Dict

from lxml.html import HtmlElement

from llm_web_kit.exception.exception import HtmlMathRecognizerException
from llm_web_kit.extractor.html.recognizer.cc_math.common import (
    CCMATH, CCMATH_INLINE, CCMATH_INTERLINE, CSDN, MathType, text_strip)
from llm_web_kit.libs.html_utils import (build_cc_element, element_to_html,
                                         replace_element)


def modify_tree(cm: CCMATH, math_render: str, o_html: str, node: HtmlElement, parent: HtmlElement):
    try:
        text = node.text
        if text and text_strip(text):
            if node.tag not in ['script', 'style']:
                new_span = create_new_span([(CCMATH_INLINE,MathType.LATEX)], cm.wrap_math_md(text), node, math_render, o_html)
                node.addnext(new_span)
            else:
                katex_pattern = re.compile(r'katex.render')
                node_text = text_strip(text)
                if katex_pattern.findall(node_text):
                    formulas_dict = extract_katex_formula(node_text)
                    for element_id, formula_content in formulas_dict.items():
                        target_elements = parent.xpath(f"//*[@id='{element_id}']")
                        if target_elements:
                            target_element = target_elements[0]
                            o_html = element_to_html(target_element)
                            target_element.text = None
                            new_span = create_new_span([(CCMATH_INLINE,MathType.LATEX)], cm.wrap_math_md(formula_content), target_element, math_render, o_html)
                            target_element.insert(0, new_span)
                elif node.get('type') and 'math/tex' in node.get('type'):
                    tag_math_type_list = cm.get_equation_type(o_html)
                    if not tag_math_type_list:
                        return
                    new_span = create_new_span(tag_math_type_list, cm.wrap_math_md(node_text), node, math_render, o_html)
                    replace_element(node, new_span)
    except Exception as e:
        raise HtmlMathRecognizerException(f'Error processing katex math: {e}')


def create_new_span(tag_math_type_list, text_content, node, math_render, o_html):
    return build_cc_element(
        html_tag_name=tag_math_type_list[0][0],
        text=text_content,
        tail=text_strip(node.tail),
        type=tag_math_type_list[0][1],
        by=math_render,
        html=o_html
    )


def extract_katex_formula(text: str) -> Dict[str, str]:
    render_pattern = re.compile(r'katex.render\s*\(\s*"([^"]*)"\s*,\s*(\w+)\s*\)\s*')
    render_matches = render_pattern.findall(text)
    formulas_dict = {element_id: formula_content for formula_content, element_id in render_matches}
    return formulas_dict


def process_katex_mathml(cm, math_render, node):
    try:
        # 根据节点class确定公式类型
        equation_type = CCMATH_INLINE if CSDN.INLINE in node.get('class') else CCMATH_INTERLINE
        # 查找内部的katex-mathml节点提取公式
        mathml_nodes = node.xpath(f'.//span[@class="{CSDN.MATH}"]')
        if mathml_nodes:
            mathml_node = mathml_nodes[0]
            # 提取latex公式（取最后一行非空内容）
            lines = [line.strip() for line in mathml_node.text_content().splitlines() if line.strip()]
            if lines:
                latex = lines[-1]
                if latex:
                    html_with_formula = element_to_html(node)
                    # 创建新元素替换原节点
                    new_span = build_cc_element(
                        html_tag_name=equation_type,
                        text=cm.wrap_math_md(latex),
                        tail=text_strip(node.tail),
                        type='latex',
                        by=math_render,
                        html=html_with_formula
                    )
                    replace_element(node, new_span)
    except Exception as e:
        raise HtmlMathRecognizerException(f'处理CSDN博客数学公式失败: {e}')


def process_zhihu_custom_tag(cm, math_render, node):
    try:
        # 从data-tex属性获取LaTeX公式
        latex = node.get('data-tex')
        if not latex:
            return
        html_with_formula = f'<span>{latex}</span>'
        tag_math_type_list = cm.get_equation_type(html_with_formula)
        # 如果无法确定类型，默认为行内公式
        if not tag_math_type_list:
            tag_math_type_list = [(CCMATH_INLINE, MathType.LATEX)]
        new_span = build_cc_element(
            html_tag_name=tag_math_type_list[0][0],
            text=cm.wrap_math_md(latex),
            tail=text_strip(node.tail),
            type=tag_math_type_list[0][1],
            by=math_render,
            html=element_to_html(node)
        )
        replace_element(node, new_span)
    except Exception as e:
        raise HtmlMathRecognizerException(f'处理知乎数学公式失败: {e}')
