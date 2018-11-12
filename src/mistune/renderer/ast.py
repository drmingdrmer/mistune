
class AstRenderer(object):
    IS_AST = True

    def heading(self, children, level):
        return {
            'type': 'heading',
            'children': children,
            'attributes': {
                'level': level,
            }
        }

    def block_code(self, text, lang):
        return {
            'type': 'block_code',
            'value': text,
            'attributes': {
                'lang': lang,
            }
        }

    def hrule(self):
        return {'type': 'hrule'}
