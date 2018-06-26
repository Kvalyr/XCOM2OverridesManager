import re
from Overrides.constants import re_mco_ml, re_xce_engine, re_mco


class IniTextProcessor(object):

    @classmethod
    def get_regex_for_ini_section(cls, ini_section_label, until_eof=False):
        pattern = r'(\[' + ini_section_label + '\][\s\S]'

        if until_eof:
            pattern += r'*)$'  # '[\s\S]*$' is "everything until EOF" when doing multiline
        else:
            pattern += r'+?)(\[.+?\])'  # 1:(SECTION_LABEL)2:(next section)
        return re.compile(pattern, flags=re.MULTILINE)

    @classmethod
    def get_existing_overrides(cls, config_text):
        match = re.search(re_mco_ml, config_text)
        if match:
            return '\n'.join(match.groups())

    @classmethod
    def clean_out_all_overrides(cls, config_text):
        any_mco = re.search(re_mco, config_text)
        if not any_mco:
            return config_text
        return re.sub(re_mco_ml, "\n[", config_text)

    @classmethod
    def repair_config_text(cls, config_text):
        # Cleanups
        # Multiple blank lines
        # config_text = re.sub('\n\n', '\n', config_text)

        text_lines = config_text.split('\n')
        repaired_lines = []
        for line in text_lines:

            # Find lines where a ModClassOverrides entry got appended to the end of a previous line instead of after a newline
            if "ModClassOverrides" in line:
                splits = line.split("ModClassOverrides")
                if splits[0] == '' or splits[0] == '+':  # Line started with ModClassOverrides, no repair needed
                    repaired_lines.append(line)
                    continue
                print("Found ModClassOverrides line that didn't begin on its own line. Repairing: ", line)
                line = splits[0] + "\n" + "ModClassOverrides" + splits[1]

            repaired_lines.append(line)

        return '\n'.join(repaired_lines)

    @classmethod
    def replace_old_overrides(cls, config_text, overrides_list):
        # overrides_text = '\n' + '\n'.join([str(o) for o in overrides_list])
        overrides_text = '\n'.join([str(o) for o in overrides_list])

        any_mco = re.search(re_mco, config_text)
        if any_mco:
            return re.sub(re_mco_ml, overrides_text + "\n\n[", config_text)
        return re.sub(re_xce_engine, r'\1' + overrides_text + "\n" + r'\2\3', config_text)
