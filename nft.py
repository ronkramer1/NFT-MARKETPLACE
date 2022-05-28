import json


class NFT:
    def __init__(self, image=None, name="", owner="", creator=""):
        self.image = image
        self.name = name
        self.owner = owner
        self.creator = creator

    def serialize(self):
        nft_dict = dict(self.__dict__)
        return str(json.dumps(nft_dict, indent=4))

    @staticmethod
    def deserialize(data):
        if type(data) == str:
            data_dict = json.loads(data)
        else:
            data_dict = data

        return NFT(data_dict["image"],
                   data_dict["name"],
                   data_dict["owner"],
                   data_dict["creator"])

    def __str__(self):
        return f"image: {self.image}\n" \
               + f"name: {self.name}\n" \
               + f"owner: {self.owner}\n" \
               + f"creator: {self.creator}\n"
