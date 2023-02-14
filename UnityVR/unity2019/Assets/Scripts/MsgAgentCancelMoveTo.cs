using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    [Serializable, ProtoContract]
    public class MsgAgentCancelMoveTo
    {
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;
    }
}
