using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    /// <summary>
    /// Sends a command created by the user controlling the VR (VR to Agent).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgMenu
    {
        /// <summary>
        /// An enum to identify the event: 0 = start simulation, 1 = stop simulation
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 eventID;

        /// <summary>
        /// A string to send additional parameters
        /// </summary>
        [ProtoMember(2)]
        public string parameter;
    }
}
