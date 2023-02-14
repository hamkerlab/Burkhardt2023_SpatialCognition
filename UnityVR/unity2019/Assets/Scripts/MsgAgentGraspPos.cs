using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Message to grasp an object at (x,y) in field of view (Agent->VR)
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgAgentGraspPos
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

    }
}
