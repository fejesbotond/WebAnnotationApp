from bson import ObjectId

class Service:
    def validate_id(self, id: str) -> bool:
        try:
            ObjectId(id)
        except:
            return False
        return True

def get_file_content(id: str) -> str:
    file_path = f"resources/files/{id}.txt"
    with open(file_path, "rb") as f:
        content = f.read()
    content = content.decode("utf-8")
    white_spaces = ['\n', ' ', '\t', '\r']
    i = 1
    res = ""
    if content[0] not in white_spaces:
        res += content[0]
    while(i<len(content)):
        if content[i] not in white_spaces:
            res+= content[i]
        elif content[i-1] not in white_spaces:
            res+= ' '
        i += 1
    return res