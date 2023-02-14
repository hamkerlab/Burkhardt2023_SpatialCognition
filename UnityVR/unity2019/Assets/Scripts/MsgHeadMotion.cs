using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    /// <summary>
    /// This delivers balance information (VR to Agent).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgHeadMotion
    {
        [ProtoMember(1, IsRequired = true)]
        public float velocityX;

        [ProtoMember(2, IsRequired = true)]
        public float velocityY;

        [ProtoMember(3, IsRequired = true)]
        public float velocityZ;

        [ProtoMember(4, IsRequired = true)]
        public float accelerationX;

        [ProtoMember(5, IsRequired = true)]
        public float accelerationY;

        [ProtoMember(6, IsRequired = true)]
        public float accelerationZ;

        [ProtoMember(7, IsRequired = true)]
        public float rotationVelocityX;

        [ProtoMember(8, IsRequired = true)]
        public float rotationVelocityY;

        [ProtoMember(9, IsRequired = true)]
        public float rotationVelocityZ;

        [ProtoMember(10, IsRequired = true)]
        public float rotationAccelerationX;

        [ProtoMember(11, IsRequired = true)]
        public float rotationAccelerationY;

        [ProtoMember(12, IsRequired = true)]
        public float rotationAccelerationZ;
    }
}