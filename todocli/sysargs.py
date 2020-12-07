import distutils.util
import sys

from error import error


class SysargParser:
    class Option:
        def __init__(self, name, is_flag, default_value, type):
            self.name = name
            self.is_flag = is_flag
            self.value = default_value
            self.type = type

        def setValue(self, val):
            if self.type == bool:
                self.value = bool(distutils.util.strtobool(val.lower()))
            else:
                self.value = self.type(val)

    def __init__(self):
        self.option_lookuptable = {}

        self.valid_options = []
        self.required_options = []

    def addOptionFlag(self, name, *option_names):
        self._addOption(name, True, False, bool, *option_names)

    def addOptionValue(self, name, default_value, type, *option_names):
        self._addOption(name, False, default_value, type, *option_names)

    def _addOption(self, name, is_flag, default_value, type, *option_names):
        option = self.Option(name, is_flag, default_value, type)

        def createLutEntry(option_name, option_obj):
            return {option_name: option_obj}

        self.valid_options.append(option)

        for x in list(option_names):
            lut_entry = createLutEntry(x, option)
            self.option_lookuptable.update(lut_entry)
            pass

    def addRequiredArgument(self, name):
        reqOption = self.Option(name, False, None, str)
        self.required_options.append(reqOption)

    def parseArgs(self):
        self.this_script_path = sys.argv[0]
        self.args = sys.argv[1:]

        required_parsing_started = False
        currently_parsing_option = None
        cur_required_argument = 0

        arglist = self.args

        for x in arglist:
            if currently_parsing_option is not None:
                currently_parsing_option.setValue(x)
                currently_parsing_option = None
            elif x.startswith('-'):
                if required_parsing_started:
                    error("Option {} wurde angegeben, nachdem ein erforderliches Argument angegeben wurde.".format(x))

                def addOption(option_name):
                    nonlocal currently_parsing_option
                    if option_name not in self.option_lookuptable:
                        error("Option {} nicht erkannt.".format(option_name))

                    option = self.option_lookuptable.get(option_name, None)
                    if option.is_flag:
                        option.value = True
                    else:
                        currently_parsing_option = option

                if x.startswith('--'):
                    addOption(x)
                else:
                    last_c = None
                    for c in x[1:]:
                        if currently_parsing_option:
                            error(f"Argument nach {last_c} erwartet.")


                        addOption(f"-{c}")
                        last_c = c
            else:
                if cur_required_argument == len(self.required_options):
                    error("Zuviele Argumente angegeben.")
                    sys.exit (-1)
                else:
                    self.required_options[cur_required_argument].setValue(x)
                    cur_required_argument += 1

        if cur_required_argument != len(self.required_options):
            error("Nicht alle Argumente angegeben.")

        self.addParametersToThisClass()

    def addParametersToThisClass(self):
        for opt in self.valid_options:
            self.__dict__[opt.name] = opt.value

        for opt in self.required_options:
            self.__dict__[opt.name] = opt.value

    def get(self, param):
        return self.__dict__[param]


args = SysargParser()