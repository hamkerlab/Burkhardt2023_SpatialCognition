using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;


namespace SimpleNetwork
{
    /// <summary>
    /// Message to compare versions of server and client
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgVersionCheck
    {
        /// <summary>
        /// string containing the version of the server
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public string version;


    }
}