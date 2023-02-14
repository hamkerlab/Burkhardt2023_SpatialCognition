using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    /// <summary>
    /// Sends stereo image data (VR to Agent).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgImages
    {

        /// <summary>
        /// The byte data of the left image in png-format
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public byte[] leftImage;

        /// <summary>
        /// The byte data of the right image in png-format
        /// </summary>
        [ProtoMember(2, IsRequired = true)]
        public byte[] rightImage;
		
		/// <summary>
        /// The byte data of the main image in png-format
        /// </summary>
        [ProtoMember(3, IsRequired = true)]
        public byte[] mainImage;
    }
}
