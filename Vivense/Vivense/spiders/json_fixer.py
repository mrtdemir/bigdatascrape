import json

class JsonFixer:
    def __init__(self, json_path):
        self.path = json_path
        json_file = self.readJsonFile(self.path)
        json_file = self.removeDuplicateKeys(json_file)
        self.writeJsonFile(self.fixer(json_file))
        print("Json dosya düzeltmesi tamamlandı.")

    def readJsonFile(self, path):
        with open(path, encoding='utf8') as f:
            return json.load(f)

    def fixer(self, json):
        temp_json = json.copy()
        for main_category in temp_json.keys():
            for data in json[main_category].keys():
                sub_data = temp_json[main_category][data]['Ürün Özellikleri']
                for key, values in sub_data.items():
                    temp = [] 
                    for value in values:
                        if value == None:
                            continue
                        fixed = value.replace('\r', '').replace('\n', '').replace('\t', '').replace('\"', "'").replace(" "," ").lstrip().rstrip()
                        fixed = ' '.join(fixed.split())
                        if fixed.rstrip(".").lower() not in [t.rstrip(".").lower() for t in temp]:
                            temp.append(fixed)
                    sub_data.update({key:temp})
                json[main_category][data]['Ürün Özellikleri'] = sub_data
        return json

    def removeDuplicateKeys(self, json):
        temp_json = json.copy()
        for main_category in temp_json.keys():
            for data in temp_json[main_category].keys():
                fixed_sub_data = dict()
                sub_data = temp_json[main_category][data]['Ürün Özellikleri']
                for key, value in sub_data.items():
                    fixed_key = key.replace('\n', '').replace('\t', '').rstrip().lstrip().lower()
                    if fixed_key not in fixed_sub_data:
                        fixed_sub_data[fixed_key] = value
                    else:
                        fixed_sub_data[fixed_key] += value
                json[main_category][data]['Ürün Özellikleri'] = fixed_sub_data
        return json

    def writeJsonFile(self, json_file):
        with open('result.json', 'w', encoding='utf8') as f:
            json.dump(json_file, f, ensure_ascii=False,indent=4)

if __name__ == '__main__':
    JsonFixer('all_products.json')