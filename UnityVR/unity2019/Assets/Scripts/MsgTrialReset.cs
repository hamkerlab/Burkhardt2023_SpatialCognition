using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Sends a command that sets the VR partly back to a chosen state (Agent to VR). This message should be used for starting a new trial in an experiment.
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgTrialReset
    {

        /// <summary>
        /// Signals the VR to perform a trialreset
        /// </summary>
        [ProtoMember(1)]
        public int Type;
    }
}

