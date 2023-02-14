using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Delivers reward to the agent (VR to Agent).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgReward
    {

        /// <summary>
        /// The user-specified external reward for the agent
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public float reward;
    }
}
