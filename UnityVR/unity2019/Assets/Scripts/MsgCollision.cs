using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;
namespace SimpleNetwork
{
    /// <summary>
    /// Detects a collision (VR to Agent)
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgCollision
    {

        /// <summary>
        /// The value to identify the current action
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;

        /// <summary>
        /// The ID of the collided item
        /// </summary>
        [ProtoMember(2, IsRequired = true)]
        public Int32 colliderID;
    }
}
