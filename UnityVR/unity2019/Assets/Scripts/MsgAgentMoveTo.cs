using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    [Serializable, ProtoContract]
    public class MsgAgentMoveTo
    {
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;

        [ProtoMember(2, IsRequired = true)]
        public float posX;

        [ProtoMember(3, IsRequired = true)]
        public float posY;

        [ProtoMember(4, IsRequired = true)]
        public float posZ;

        [ProtoMember(5)]
        public Int32 targetMode;
    }
}
