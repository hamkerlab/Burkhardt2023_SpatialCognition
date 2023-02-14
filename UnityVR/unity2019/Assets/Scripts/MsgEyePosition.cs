using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    /// <summary>
    /// This delivers the eye rotation and velocity of the agent (VR to Agent).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgEyePosition
    {
        [ProtoMember(1, IsRequired = true)]
        public float rotationPositionX;

        [ProtoMember(2, IsRequired = true)]
        public float rotationPositionY;

        [ProtoMember(3, IsRequired = true)]
        public float rotationPositionZ;

        [ProtoMember(4, IsRequired = true)]
        public float rotationVelocityX;

        [ProtoMember(5, IsRequired = true)]
        public float rotationVelocityY;

        [ProtoMember(6, IsRequired = true)]
        public float rotationVelocityZ;
    }
}