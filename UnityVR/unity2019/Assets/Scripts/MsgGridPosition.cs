using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    /// <summary>
    /// This delivers the coordinates and rotation of the agent, like a GPS device (VR to Agent).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgGridPosition
    {

        /// <summary>
        /// The X-coordinate of the agent
        /// </summary>
        [ProtoMember(1, IsRequired=true)]
        public float targetX;

        /// <summary>
        /// The Y-coordinate of the agent
        /// </summary>
        [ProtoMember(2, IsRequired=true)]
        public float targetY;

        /// <summary>
        /// The Z-coordinate of the agent
        /// </summary>
        [ProtoMember(3, IsRequired=true)]
        public float targetZ;

        /// <summary>
        /// The rotation around the X-axis of the agent
        /// </summary>
        [ProtoMember(4, IsRequired = true)]
        public float targetRotationX;

        /// <summary>
        /// The rotation around the Y-axis of the agent
        /// </summary>
        [ProtoMember(5, IsRequired = true)]
        public float targetRotationY;

        /// <summary>
        /// The rotation around the Z-axis of the agent
        /// </summary>
        [ProtoMember(6, IsRequired = true)]
        public float targetRotationZ;

    }
}
