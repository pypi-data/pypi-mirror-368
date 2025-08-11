import configparser
import io

C_BRACING_STYLES = ['bsd', 'knr']

def _read_bool(config, section, key):
    try:
        ret = config[section].getboolean(key)
    except ValueError:
        raise ValueError(f"Invalid value ({config[section][key]}) for boolean option {key}")

    config.remove_option(section, key)
    return ret
    
class DuckargsConfig(object):
    def __init__(self, c_header_comment=True, c_printing_code=True, c_bracing_style='bsd',
                 python_header_comment=True, python_printing_code=True):
        self.c_header_comment = c_header_comment
        self.c_printing_code = c_printing_code
        self.c_bracing_style = c_bracing_style

        self.python_printing_code = python_printing_code
        self.python_header_comment = python_header_comment

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as fh:
            return cls.from_string(fh.read())

    @classmethod
    def from_string(cls, string):
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option
        config.read_string(string)
        kwargs = {}

        if "C" in config:
            if 'HeaderComment' in config["C"]:
                kwargs['c_header_comment'] = _read_bool(config, "C", 'HeaderComment')

            if 'PrintingCode' in config["C"]:
                kwargs['c_printing_code'] = _read_bool(config, "C", 'PrintingCode')

            if 'BracingStyle' in config["C"]:
                brace_style = config["C"]["BracingStyle"].lower()
                if brace_style not in C_BRACING_STYLES:
                    raise RuntimeError(f"Invalid C bracing style ({brace_style}). "
                                        "Valid brace styles are: {C_BRACING_STYLES}")

                config.remove_option('C', 'BracingStyle')
                kwargs['c_bracing_style'] = brace_style

            if len(config["C"]) > 0:
                raise ValueError(f"Unrecognized C option(s) in {filename}: {config.items('C')}")

            config.remove_section("C")

        if "Python" in config:
            if 'HeaderComment' in config["Python"]:
                kwargs['python_header_comment'] = _read_bool(config, "Python", 'HeaderComment')

            if 'PrintingCode' in config["Python"]:
                kwargs['python_printing_code'] = _read_bool(config, "Python", 'PrintingCode')

            if len(config["Python"]) > 0:
                raise ValueError(f"Unrecognized Python option(s) in {filename}: {config.items('Python')}")

            config.remove_section("Python")

        if len(config.sections()) > 0:
            raise ValueError(f"Unrecognized section(s) in {filename}: {config.sections()}")

        return DuckargsConfig(**kwargs)

    def to_string(self):
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option

        config["C"] = {
            "HeaderComment": "true" if self.c_header_comment else "false",
            "PrintingCode": "true" if self.c_printing_code else "false",
            "BracingStyle": self.c_bracing_style
        }

        config["Python"] = {
            "HeaderComment": "true" if self.python_header_comment else "false",
            "PrintingCode": "true" if self.python_printing_code else "false"
        }

        buf = io.StringIO()
        config.write(buf)
        return buf.getvalue()

    def to_file(self, filename):
        with open(filename, 'w') as fh:
            fh.write(self.to_string())

if __name__ == "__main__":
    cfg = DuckargsConfig.from_file("test_config.ini")
    print(cfg.to_string())
    #cfg.save("test_config.ini")
    
