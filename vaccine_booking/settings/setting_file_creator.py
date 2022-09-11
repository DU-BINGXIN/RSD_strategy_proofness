import pdb
import pandas as pd
import json
import click


class SettingFileCreator:
    """
    4つのjsonファイル（inputs_global_settings, inputs_message_structure,
    inputs_organizations, inputs_sites）からsettingsのjsonファイルを作成
    """

    def __init__(self):
        self.organization_settings = {}
        self.global_settings = {}
        self.path = "settings/inputs_for_creator/"

    # jsonファイルの読み込み
    def read_inputs_from_json(self, input_name):
        file_path = f"{self.path}{input_name}.json"
        with open(file_path) as f:
            input_dict = json.load(f)
        return input_dict

    # global_settingsに関する情報を入力
    def _set_global_settings(self):
        self.global_settings = self.read_inputs_from_json("inputs_global_settings")

    # organizationsに関する情報を入力
    def _set_organizations(self):
        organizations_settings = self.read_inputs_from_json("inputs_organizations")
        for key, values in organizations_settings.items():
            self.organization_settings[key] = values

    # 各organizationsにsite関する情報を入力
    def _set_sites(self):
        sites_settings = self.read_inputs_from_json("inputs_sites")
        # 各組織の属性（algorithm, site_list, message_structure)を取得
        for org_name, org_attributes in self.organization_settings.items():
            # 各組織のsiteのlistをもとに、inputs_sitesの情報を入力
            org_sites = {}
            for site in org_attributes["site_list"]:
                org_sites[site] = sites_settings[site]
            org_attributes["sites"] = org_sites

    # 各organizationsにメッセージ関する情報を入力
    def _set_messages(self):
        message_structure = self.read_inputs_from_json("inputs_message_structure")
        # 各組織の属性（algorithm, site_list, message_structure)を取得
        for org_name, org_attributes in self.organization_settings.items():
            # 各組織のsiteに対してメッセージを設定。メッセージの構造はinputs_message_structureから取得
            org_attributes["messages"] = {}
            for site in org_attributes["site_list"]:
                for message_name, message_elements in message_structure[
                    org_attributes["message_type"]
                ].items():
                    org_message = {}
                    org_message["site"] = site
                    org_message["day"] = message_elements["day"]
                    org_message["time"] = message_elements["time"]
                    org_attributes["messages"][f"{site}_{message_name}"] = org_message
            # site_listとmessage_structureに関する情報を削除（settingsに不要なため）
            del self.organization_settings[org_name]["message_type"]
            del self.organization_settings[org_name]["site_list"]

    # jsonファイルの出力
    def make_json_file(self):
        self._set_global_settings()
        self._set_organizations()
        self._set_sites()
        self._set_messages()

        settings = {}
        settings["global_settings"] = self.global_settings
        # jsonファイルの名前を取得
        settings_file_name = settings["global_settings"]["settings_name"]
        # settings_nameに関する情報を削除（settingsに不要なため）
        del settings["global_settings"]["settings_name"]
        # 組織の情報を統合
        settings.update(self.organization_settings)

        with open(f"settings/{settings_file_name}.json", "w") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)


@click.command()
def main():
    settingfile_creator = SettingFileCreator()
    settingfile_creator.make_json_file()


if __name__ == "__main__":
    main()
