using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Message to point at an object by ID
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgAgentPointID
    {
        /// <summary>
        /// A randomized value to identify the action
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;

        /// <summary>
        /// ID of the object to point to
        /// </summary>
        [ProtoMember(2, IsRequired = true)]
        public Int32 objectID;

    }
}
