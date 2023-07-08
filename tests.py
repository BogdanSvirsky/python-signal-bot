from api.binance_api import BinanceAPI


def test_api(api: BinanceAPI) -> None:
    account: dict = api.get_account()
    if account is None:
        raise Exception("BinanceAPI doesn't work!")
    else:
        print("BinanceAPI is working")


def hello():
    print("Hello!")


def test():
    return hello

hell = test()
hell()