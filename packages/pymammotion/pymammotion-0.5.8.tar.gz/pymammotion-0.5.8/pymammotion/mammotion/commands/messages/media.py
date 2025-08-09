# === sendOrderMsg_Media ===
from abc import ABC

from pymammotion.mammotion.commands.abstract_message import AbstractMessage
from pymammotion.proto import (
    MUL_LANGUAGE,
    MUL_SEX,
    LubaMsg,
    MsgAttr,
    MsgCmdType,
    MsgDevice,
    MulSetAudio,
    MulSetWiper,
    SocMul,
)


class MessageMedia(AbstractMessage, ABC):
    def send_order_msg_media(self, mul):
        luba_msg = LubaMsg(
            msgtype=MsgCmdType.MUL,
            sender=MsgDevice.DEV_MOBILEAPP,
            rcver=self.get_msg_device(MsgCmdType.MUL, MsgDevice.SOC_MODULE_MULTIMEDIA),
            msgattr=MsgAttr.REQ,
            seqs=self.seqs.increment_and_get() & 255,
            version=1,
            subtype=self.user_account,
            mul=mul,
        )

        return luba_msg.SerializeToString()

    def set_car_volume(self, volume: int):
        """Set the car volume. 0 - 100"""
        return self.send_order_msg_media(SocMul(set_audio=MulSetAudio(at_switch=volume)))

    def set_car_voice_language(self, language_type: MUL_LANGUAGE | str | None):
        return self.send_order_msg_media(SocMul(set_audio=MulSetAudio(au_language=language_type)))

    def set_car_volume_sex(self, sex: MUL_SEX):
        return self.send_order_msg_media(SocMul(set_audio=MulSetAudio(sex=sex)))

    def set_car_wiper(self, round_num: int):
        """Set mower wiper."""
        # 2
        return self.send_order_msg_media(SocMul(set_wiper=MulSetWiper(round=round_num)))

    # TODO add lamp methods
