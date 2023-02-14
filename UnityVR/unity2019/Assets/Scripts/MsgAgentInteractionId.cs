using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Message to interact with an object by ID (Agent->VR)
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgAgentInteractionID
    {
        /// <summary>
        /// A randomized value to identify the action
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;

        /// <summary>
        /// ID of the object to interact with
        /// </summary>
        [ProtoMember(2, IsRequired = true)]
        public Int32 objectID;

    }
}
