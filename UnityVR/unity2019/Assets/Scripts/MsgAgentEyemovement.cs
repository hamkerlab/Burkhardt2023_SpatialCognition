using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// This command rotates the eyes of the agent (Agent to VR).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgAgentEyemovement
    {
        /// <summary>
        /// A randomized value to identify the action.
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;

        /// <summary>
        /// The rotation angle of the left eye in horizontal direction (-30 to +30)
        /// </summary>
        [ProtoMember(2, IsRequired = true)]
        public float panLeft;

        /// <summary>
        /// The rotation angle of the right eye in horizontal direction (-30 to +30)
        /// </summary>
        [ProtoMember(3, IsRequired = true)]
        public float panRight;

        /// <summary>
        /// The rotation angle of the left and right eye in vertical direction (-30 to +30)
        /// </summary>
        [ProtoMember(4)]
        public float tilt;
    }
}
