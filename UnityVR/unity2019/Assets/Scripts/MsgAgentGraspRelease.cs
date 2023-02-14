using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Message to release the grasp
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgAgentGraspRelease
    {
        /// <summary>
        /// A randomized value to identify the action
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;
    }
}
