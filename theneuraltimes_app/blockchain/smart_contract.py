import json

import requests
from decouple import config
from django.http import HttpResponseNotFound, HttpResponse
from web3 import Web3

from theneuraltimes.settings import BASE_DIR
from theneuraltimes_app.models import NFT

provider = f'https://polygon-mainnet.infura.io/v3/{config("WEB3_INFURA_PROJECT_ID")}'

web3 = Web3(Web3.HTTPProvider(provider))

contract_address = config("CONTRACT_ADDRESS")

web3.eth.account.enable_unaudited_hdwallet_features()
owner = web3.eth.account.from_mnemonic(config("CONTRACT_OWNER_MNEMONIC"))

with open(str(BASE_DIR) + '/theneuraltimes_app/blockchain/abis/TheNeuralTimes.json', 'r') as abi_definition:
    abi = json.load(abi_definition)['abi']

contract = web3.eth.contract(address=contract_address, abi=abi)


def metadata(request, nft_id: int):
    if 1 <= nft_id <= contract.functions.totalSupply().call():
        return HttpResponse(open(str(BASE_DIR) + f'/theneuraltimes_app/blockchain/metadata/{nft_id}.json', 'r'),
                            content_type='application/json; charset=utf8')
    else:
        return HttpResponseNotFound()


def upload_file_to_pinata(url_to_file: str) -> str:
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": config("PINATA_API_KEY"),
        "pinata_secret_api_key": config("PINATA_SECRET_API_KEY"),
    }
    files = {"file": bytes(requests.get(url_to_file).content)}
    response = requests.post(url=url, files=files, headers=headers)
    return response.json()['IpfsHash']


def create_metadata(nft: NFT):
    news_source = nft.pictureGenerationSuggestion.newsSuggestion.newsSource.sourceType
    news_url = nft.pictureGenerationSuggestion.newsSuggestion.url
    image_url = f"https://gateway.pinata.cloud/ipfs/{upload_file_to_pinata(nft.pictureGenerationSuggestion.picturePath)}"
    name = f"{news_source}: {nft.pictureGenerationSuggestion.newsSuggestion.headline}"
    json_dict = {
        "attributes": [
            {
                "trait_type": "News source",
                "value": news_source
            },
        ],
        "external_url": news_url,
        "image": image_url,
        "name": name,
    }
    json_str = json.dumps(json_dict)
    with open(str(BASE_DIR) + f"/theneuraltimes_app/blockchain/metadata/{nft.blockchain_id}.json", "w+") as file:
        file.write(json_str)


def mint_nft(nft: NFT):
    cur_total_supply = contract.functions.totalSupply().call()
    nft.blockchain_id = cur_total_supply + 1
    nft.save()
    create_metadata(nft)
    contract.functions.changeMaxSupply(cur_total_supply + 1).transact({'from': owner.address})
    contract.functions.mint(owner.address, 1).transact({'from': owner.address})
