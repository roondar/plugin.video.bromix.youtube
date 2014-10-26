from resources.lib.youtube import Client

__author__ = 'bromix'

import unittest

class TestClient(unittest.TestCase):
    def setUp(self):
        pass

    def test_sig(self):
        """
        a = a.split("");
        gk.KO(a, 2);
        gk.aJ(a, 52);
        gk.KO(a, 3);
        gk.aJ(a, 7);
        gk.KO(a, 3);
        gk.aJ(a, 4);
        gk.Gs(a, 2);
        return a.join("")


        {aJ: function(a) {
            a.reverse()
        },KO: function(a, b) {
            a.splice(0, b)
        },Gs: function(a, b) {
            var c = a[0];
            a[0] = a[b % a.length];
            a[b] = c

        :return:
        """

        def _aJ(a, b):
            return a[::-1]

        def _KO(a, b):
            del a[:b]
            return a

        def _Gs(a, b):
            c = a[0]
            a[0] = a[b % len(a)]
            a[b] = c
            return a

        sig_in = 'F1F16F1637D0E442F002A929015EA750047F101830867.325D777D3C576FEFC4222C17CBBEAAED0B28DD8ED8E'
        a = list(sig_in)  # a = a.split("");
        a = _KO(a, 2)
        a = _aJ(a, 52)
        a = _KO(a, 3)
        a = _aJ(a, 7)
        a = _KO(a, 3)
        a = _aJ(a, 4)
        a = _Gs(a, 2)

        signature = ''.join(a)

        """
        alr: "yes"
        mime: "video%2Fmp4"
        ratebypass: "yes"
        signature: "D8ED82B0DEAAEBBC71C2224CFEF675C3D777D523.768038101F740057AE510929A200F244E0D7361F"
        __proto__: Object
        """

        self.assertEqual('D8ED82B0DEAAEBBC71C2224CFEF675C3D777D523.768038101F740057AE510929A200F244E0D7361F', signature)
        pass

    def test_get_playlist_items(self):
        client = Client()

        json_data = client.get_playlist_items_v3('PL024E341A0495DF9F')
        pass

    def test_get_playlists(self):
        client = Client()

        json_data = client.get_playlists_v3('UCLx053rWZxCiYWsBETgdKrQ')
        pass

    def test_get_video_info_tv(self):
        client = Client()

        # vevo
        streams = client.get_video_info_tv('O-zpOMYRi0w')

        # free
        streams = client.get_video_info_tv('Y0noFhiUh1U')
        pass

    def test_get_videos_v3(self):
        client = Client()

        json_data = client.get_videos_v3(['vyD70Huufco', 'AFdezM3_m-c'])
        pass

    def test_search_v3(self):
        client = Client()

        json_data = client.search_v3(q='batman')
        pass

    def test_get_what_to_watch_tv(self):
        client = Client()

        # 'Popular on YouTube'
        json_data = client.get_what_to_watch_tv()
        pass

    def test_get_channel_sections_v3(self):
        client = Client()

        # 'Lazy Game Reviews'
        json_data = client.get_channel_sections_v3(channel_id='UCLx053rWZxCiYWsBETgdKrQ')

        # 'Popular on YouTube'
        json_data = client.get_channel_sections_v3(channel_id='UCF0pVplsI8R5kcAqgtoRqoA')

        # 'Sports'
        json_data = client.get_channel_sections_v3(channel_id='UCEgdi0XIXXZ-qJOFPf4JSKw')

        # TODO: the first playlist of the section is the content of the 'HOME' and YouTube TV section
        pass

    def test_get_channels_v3(self):
        client = Client()

        # 'Lazy Game Reviews'
        json_data = client.get_channels_v3(channel_id='UCLx053rWZxCiYWsBETgdKrQ')

        # 'Popular on YouTube', 'Sport'
        json_data = client.get_channels_v3(channel_id=['UCF0pVplsI8R5kcAqgtoRqoA','UCEgdi0XIXXZ-qJOFPf4JSKw'])
        pass

    def test_get_guide_v3(self):
        client = Client()

        json_data = client.get_guide_v3()
        pass

    def test_get_guide_tv(self):
        client = Client()

        json_data = client.get_guide_tv()
        pass

    pass
