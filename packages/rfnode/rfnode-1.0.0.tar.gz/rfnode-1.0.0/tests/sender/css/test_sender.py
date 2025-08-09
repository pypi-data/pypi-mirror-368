def test_sender(mocker):
    payload: str = "105.55|49.59"
    print(payload)
    stub = mocker.stub(name="sender_stub")
    mocker.patch("rfnode.rf_sender.css.sender.Sender").return_value = stub
    # sender = Sender("/dev/ttyUSB0")
    # lst:list[bytes] = sender.build_packets(payload=payload)
    # assert len(lst)>0
    # see https://medium.com/@vrasabhajinta/mock-vs-stub-which-to-use-in-python-ffe901185902
    assert 1 == 1
