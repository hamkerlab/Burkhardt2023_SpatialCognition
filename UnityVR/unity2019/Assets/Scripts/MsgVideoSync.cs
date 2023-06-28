using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Flag to signal if the agent should only move small steps and wait aftererwards
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgVideoSync
    {
        [ProtoMember(1)]
        public int i;
    }
}

