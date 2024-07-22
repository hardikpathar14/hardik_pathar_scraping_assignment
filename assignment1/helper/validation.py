class Validation():
    def __init__(self):
        pass

    def main(self, incoming_data):
        if incoming_data["availability"] == "InStock":
            if incoming_data["product_id"] and incoming_data["title"] and incoming_data["models"]["variants"]:
                temp_list = list()
                for each_value in incoming_data["models"]["variants"]:
                    if each_value["image"] and each_value["price"]:
                        temp_list.append(each_value)
                if temp_list:
                    incoming_data["models"]["variants"] = temp_list
                    return incoming_data