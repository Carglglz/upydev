from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal


cyan = "#56b6c2"
blue = "#61afef"
purple = "#c678dd"
green = "#98c379"
red_1 = "#e06c75"
red_2 = "#be5046"
orange_1 = "#d19a66"
orange_2 = "#e5c07b"

class Monokai_darkStyle(Style):
    """
    This style mimics the Monokai color scheme.
    """

    background_color = "#000000"
    highlight_color = "#49483e"

    styles = {
        # No corresponding class for the following:
        Text:                      "#f8f8f2", # class:  ''
        Whitespace:                "",        # class: 'w'
        Error:                     "#960050 bg:#1e0010", # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   "#75715e", # class: 'c'
        Comment.Multiline:         "",        # class: 'cm'
        Comment.Preproc:           "",        # class: 'cp'
        Comment.Single:            "",        # class: 'c1'
        Comment.Special:           "",        # class: 'cs'

        Keyword:                   "#66d9ef", # class: 'k'
        Keyword.Constant:          "",        # class: 'kc'
        Keyword.Declaration:       "",        # class: 'kd'
        Keyword.Namespace:         "#f92672", # class: 'kn'
        Keyword.Pseudo:            "",        # class: 'kp'
        Keyword.Reserved:          "",        # class: 'kr'
        Keyword.Type:              "",        # class: 'kt'

        Operator:                  "#f92672", # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               "#f8f8f2", # class: 'p'

        Name:                      "#f8f8f2", # class: 'n'
        Name.Attribute:            "#a6e22e", # class: 'na' - to be revised
        Name.Builtin:              "",        # class: 'nb'
        Name.Builtin.Pseudo:       "",        # class: 'bp'
        Name.Class:                "#a6e22e", # class: 'nc' - to be revised
        Name.Constant:             "#66d9ef", # class: 'no' - to be revised
        Name.Decorator:            "#a6e22e", # class: 'nd' - to be revised
        Name.Entity:               "",        # class: 'ni'
        Name.Exception:            "#a6e22e", # class: 'ne'
        Name.Function:             "#a6e22e", # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            "",        # class: 'nn' - to be revised
        Name.Other:                "#a6e22e", # class: 'nx'
        Name.Tag:                  "#f92672", # class: 'nt' - like a keyword
        Name.Variable:             "",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    "#ae81ff", # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "#ae81ff", # class: 'l'
        Literal.Date:              "#e6db74", # class: 'ld'

        String:                    "#e6db74", # class: 's'
        String.Backtick:           "",        # class: 'sb'
        String.Char:               "",        # class: 'sc'
        String.Doc:                "",        # class: 'sd' - like a comment
        String.Double:             "",        # class: 's2'
        String.Escape:             "#ae81ff", # class: 'se'
        String.Heredoc:            "",        # class: 'sh'
        String.Interpol:           "",        # class: 'si'
        String.Other:              "",        # class: 'sx'
        String.Regex:              "",        # class: 'sr'
        String.Single:             "",        # class: 's1'
        String.Symbol:             "",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "#f92672", # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "",        # class: 'gr'
        Generic.Heading:           "",        # class: 'gh'
        Generic.Inserted:          "#a6e22e", # class: 'gi'
        Generic.Output:            "",        # class: 'go'
        Generic.Prompt:            "",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "#75715e", # class: 'gu'
        Generic.Traceback:         "",        # class: 'gt'
    }


class one_darkStyle(Style):
    """
    This style mimics the atom one_dark color scheme.
    """

    background_color = "#000000"
    highlight_color = "#49483e"

    styles = {
        # No corresponding class for the following:
        Text:                      "#f8f8f2", # class:  ''
        Whitespace:                "",        # class: 'w'
        Error:                     "#960050 bg:#1e0010", # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   "#75715e", # class: 'c'
        Comment.Multiline:         "",        # class: 'cm'
        Comment.Preproc:           "",        # class: 'cp'
        Comment.Single:            "",        # class: 'c1'
        Comment.Special:           "",        # class: 'cs'

        Keyword:                   purple, # class: 'k'
        Keyword.Constant:          "",        # class: 'kc'
        Keyword.Declaration:       "",        # class: 'kd'
        Keyword.Namespace:         purple, # class: 'kn'
        Keyword.Pseudo:            "",        # class: 'kp'
        Keyword.Reserved:          "",        # class: 'kr'
        Keyword.Type:              "",        # class: 'kt'

        Operator:                  purple, # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               "#ffffff", # class: 'p'

        Name:                      "#f8f8f2", # class: 'n'
        Name.Attribute:            blue, # class: 'na' - to be revised
        Name.Builtin:              "",        # class: 'nb'
        Name.Builtin.Pseudo:       "",        # class: 'bp'
        Name.Class:                orange_2, # class: 'nc' - to be revised
        Name.Constant:             orange_2, # class: 'no' - to be revised
        Name.Decorator:            purple, # class: 'nd' - to be revised
        Name.Entity:               "",        # class: 'ni'
        Name.Exception:            orange_2, # class: 'ne'
        Name.Function:             blue, # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            "",        # class: 'nn' - to be revised
        Name.Other:                orange_2, # class: 'nx'
        Name.Tag:                  "#f92672", # class: 'nt' - like a keyword
        Name.Variable:             "",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    orange_1, # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "#ae81ff", # class: 'l'
        Literal.Date:              "#e6db74", # class: 'ld'

        String:                    green, # class: 's'
        String.Backtick:           "",        # class: 'sb'
        String.Char:               "",        # class: 'sc'
        String.Doc:                "",        # class: 'sd' - like a comment
        String.Double:             "",        # class: 's2'
        String.Escape:             "#ae81ff", # class: 'se'
        String.Heredoc:            "",        # class: 'sh'
        String.Interpol:           "",        # class: 'si'
        String.Other:              "",        # class: 'sx'
        String.Regex:              "",        # class: 'sr'
        String.Single:             "",        # class: 's1'
        String.Symbol:             "",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "#f92672", # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "",        # class: 'gr'
        Generic.Heading:           "",        # class: 'gh'
        Generic.Inserted:          orange_2, # class: 'gi'
        Generic.Output:            "",        # class: 'go'
        Generic.Prompt:            "",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "#75715e", # class: 'gu'
        Generic.Traceback:         "",        # class: 'gt'
    }
