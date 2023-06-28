# sd-webui-prompt-sub-rule
Create and manage prompt substituion rules; extension for sd-webui.

## Rule syntax

Consider the case where a rule named `Example` is defined as following.

```text
# Note: currently names specified after "rule:" doesn't serve any function. 
rule: Rule Name 1
for: foo <lora:foo:1>
tag: foo, foo alias 1, foo alias 2, foo alias 3

rule: Rule Name 2
for: bar <lora:bar:1>
tag: bar, bar alias 1, bar alias 2, bar alias 3
```

When this rule is added as a default rule, then the prompt `foo alias 1, (bar alias 2)` will be changed to `<lora:foo:1><lora:bar:1>foo, (bar)`.