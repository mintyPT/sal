# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/03_cli.ipynb.

# %% auto 0
__all__ = ['render']

# %% ../nbs/03_cli.ipynb 4
def render(file, templates):
    path = Path(templates)
    glob = path.glob('*.jinja2')

    templates_raw = {}
    for p in glob:
        model_name = p.name.replace('.jinja2', '')
        with open(p, 'r') as h:
            tpl = h.read()
        templates_raw[model_name] = tpl
        
    
    template_renderer2 = TemplateLoader(templates=templates_raw)
    
    with open(file, 'r') as h:
        xml = h.read()
        
    struct: Data = xml_to_data(xml)  
    sal = Sal(template_renderer2)
    return sal.process(struct.clone())      

