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
        /// if i == 1 -> linear saccade
        /// </summary>
        [ProtoMember(1)]
        public int i;
    }
}

