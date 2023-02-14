using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Executes a movement of the agent (Agent to VR).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgAgentMovement
    {
        /// <summary>
        /// A randomizied value to identify the action
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;
         /// <summary>
         /// The direction to walk in degree(0 to 360). This direction is relative
         /// to the world or global coordinate system.
         /// </summary>
        [ProtoMember(2, IsRequired = true)]
	    public float degree;
        /// <summary>
        /// The distance to walk
        /// </summary>
        [ProtoMember(3, IsRequired = true)]
	    public float distance;
    }
}
