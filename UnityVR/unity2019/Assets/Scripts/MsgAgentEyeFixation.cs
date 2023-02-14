using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// This command fixates the eyes at a certain point (Agent to VR) in the world coordinate system.
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgAgentEyeFixation
    {
        /// <summary>
        /// A randomized value to identify the action
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;

        /// <summary>
        /// The X-coordinate of the target point
        /// </summary>
        [ProtoMember(2, IsRequired = true)]
        public float targetX;

        /// <summary>
        /// The Y-coordinate of the target point
        /// </summary>
        [ProtoMember(3, IsRequired = true)]
        public float targetY;

        /// <summary>
        /// The Z-coordinate of the target point
        /// </summary>
        [ProtoMember(4, IsRequired = true)]
        public float targetZ;
    }
}
