using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    /// <summary>
    /// This delivers the object positions
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgObjectPosition
    {
        [ProtoMember(1, IsRequired = true)]
        public float greenCraneX;

        [ProtoMember(2, IsRequired = true)]
        public float greenCraneY;

        [ProtoMember(3, IsRequired = true)]
        public float yellowCraneX;

        [ProtoMember(4, IsRequired = true)]
        public float yellowCraneY;

        [ProtoMember(5, IsRequired = true)]
        public float greenRacecarX;

        [ProtoMember(6, IsRequired = true)]
        public float greenRacecarY;
    }
}
