using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ProtoBuf;

namespace SimpleNetwork
{
    /// <summary>
    /// Delivers the execution status of the last action (VR to Agent).
    /// </summary>
    [Serializable, ProtoContract]
    public class MsgActionExecutionStatus
    {

        /// <summary>
        /// The value to identify the action
        /// </summary>
        [ProtoMember(1, IsRequired = true)]
        public Int32 actionID;

        /// <summary>
        /// An enum describing the execution status of the action: 0= in execution; 1 =finished
        /// </summary>
        [ProtoMember(2, IsRequired = true)]
        public Int32 status;

        public const int InExecution = 0;
        public const int Finished = 1;
        public const int Aborted = 2;
        public const int Walking = 3;
        public const int Rotating = 4;
        public const int WalkingRotating = 5;
    }
}
