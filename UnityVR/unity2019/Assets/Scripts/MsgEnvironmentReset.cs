using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Sends a command that sets the VR back to an chosen state (Agent to VR). This message should be used for restarting the whole experiment.
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgEnvironmentReset
    {

        /// <summary>
        /// Signals the VR to perform a Reset
        /// </summary>
        [ProtoMember(1)]
        public int Type;
    }
}

