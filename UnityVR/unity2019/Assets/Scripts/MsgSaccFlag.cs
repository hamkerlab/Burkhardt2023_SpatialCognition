using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Flag to perform a linear saccade
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgSaccFlag
    {

        /// <summary>
        /// Signals the VR to perform a Reset
        /// </summary>
        [ProtoMember(1)]
        public int i;
    }
}

