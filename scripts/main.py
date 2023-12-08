import os

import modules.scripts as scripts
import gradio as gr

from modules import script_callbacks, shared

from storage import Storage
from replacer import Replacer

shared.opts.add_option("enable_prompt_sub_rules", shared.OptionInfo("", "Enable prompt substitution", gr.Checkbox, section=(None, '')))
shared.opts.add_option("prompt_sub_rules", shared.OptionInfo("", "Default prompt substitution rules", gr.Textbox, section=(None, '')))

storage_rule = Storage(os.path.join(scripts.basedir(), "rule"))
storage_ruleset = Storage(os.path.join(scripts.basedir(), "ruleset"))

class Script(scripts.Script):
    def __init__(self):
        super().__init__()
    
    def title(self):
        return "Prompt Sub Rule"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        return ()

    def process(self, p):
        if not getattr(shared.opts, 'enable_prompt_sub_rules', False):
            return

        replacer = Replacer()

        for sub_rule_name in getattr(shared.opts, 'prompt_sub_rules', "").split(','):
            replacer.add_rule(storage_rule.get(sub_rule_name))

        p.all_prompts = [replacer.replace(prompt) for prompt in p.all_prompts]


class Interface:
    in_rule_name = None
    in_ruleset_value = None

    @classmethod
    def list_rules(cls, include_blank=True):
        rules = storage_rule.items
        if include_blank: rules = [''] + rules
        return rules

    @classmethod
    def list_rulesets(cls, include_blank=True):
        rulesets = storage_ruleset.items
        if include_blank: rulesets = [''] + rulesets
        return rulesets

    @classmethod
    def load_rule(cls, rule_name):
        return storage_rule.get(rule_name)

    @classmethod
    def save_rule(cls, rule_name, rule):
        storage_rule.put(rule_name, rule)
        return cls.get_gr_update_rule()

    @classmethod
    def delete_rule(cls, rule_name):
        storage_rule.delete(rule_name)
        return cls.get_gr_update_rule()

    @classmethod
    def get_gr_update_rule(cls):
        return [
            gr.update(choices=cls.list_rules()),
            gr.update(choices=cls.list_rules(False)),
            # gr.update(choices=cls.list_rules(False)),
        ]

    @classmethod
    def get_default_rules(cls):
        return [x.strip() for x in getattr(shared.opts, 'prompt_sub_rules', "").split(',') if x.strip()]

    @classmethod
    def update_default_rules(cls, rules):
        shared.opts.set('prompt_sub_rules', ",".join(rules))

    @classmethod
    def create_rule_ui(cls):
        with gr.Box(elem_classes="ch_box"):
            gr.Markdown("### Rule")
            with gr.Row():
                with gr.Column():
                    cls.in_rule_name = gr.Dropdown(cls.list_rules(), label="Name", allow_custom_value=True)
                with gr.Column():
                    cls.btn_save_rule = gr.Button("Save")
                    cls.btn_delete_rule = gr.Button("Delete")
            with gr.Row():
                cls.in_rule = gr.Textbox(lines=5, max_lines=40, label="Rule")
            with gr.Row():
                cls.in_default_rules = gr.Dropdown(cls.list_rules(False), label="Default Rules", multiselect=True, value=cls.get_default_rules)

    @classmethod
    def create_ruleset_ui(cls):
        with gr.Box(elem_classes="ch_box"):
            gr.Markdown("### Ruleset")
            with gr.Row():
                with gr.Column():
                    cls.in_ruleset_name = gr.Dropdown(cls.list_rulesets(), label="Name", allow_custom_value=True)
                    cls.in_ruleset_value = gr.Dropdown(cls.list_rules(False), label="Rules", multiselect=True)
                with gr.Column():
                    gr.Button("Save")
                    gr.Button("Delete")
            with gr.Row():
                cls.in_default_ruleset = gr.Dropdown(cls.list_rulesets(), label="Default Ruleset")

    @classmethod
    def init_ui_handler(cls):
        # rule_list_updates = [cls.in_rule_name, cls.in_default_rules, cls.in_ruleset_value]
        rule_list_updates = [cls.in_rule_name, cls.in_default_rules]
        cls.in_rule_name.change(cls.load_rule, inputs=cls.in_rule_name, outputs=cls.in_rule)
        cls.btn_save_rule.click(cls.save_rule, inputs=[cls.in_rule_name, cls.in_rule], outputs=rule_list_updates)
        cls.btn_delete_rule.click(cls.delete_rule, inputs=[cls.in_rule_name], outputs=rule_list_updates)

        cls.in_default_rules.change(cls.update_default_rules, inputs=cls.in_default_rules)

    @classmethod
    def on_ui_tabs(cls):
        with gr.Blocks(analytics_enabled=False) as prompt_sub_rule_tab:
            with gr.Box(elem_classes="ch_box"):
                with gr.Row():
                    checkbox_enable = gr.Checkbox((lambda: getattr(shared.opts, 'enable_prompt_sub_rules', False)), label="Enable")
                    checkbox_enable.change((lambda enabled: shared.opts.set('enable_prompt_sub_rules', enabled)), inputs=checkbox_enable)
            cls.create_rule_ui()
            # cls.create_ruleset_ui()
            cls.init_ui_handler()
        return [(prompt_sub_rule_tab, "Prompt Sub Rule", "prompt_sub_rule")]

script_callbacks.on_ui_tabs(Interface.on_ui_tabs)
