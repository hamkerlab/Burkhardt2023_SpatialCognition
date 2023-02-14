using System.Xml;
using System.Xml.Serialization;

using UnityEngine;

namespace XMLSerializer
{
    public class Vertex
    {
        [XmlAttribute("index")]
        public int index;

        public v3 WorldSpace;

        public v3 EyeSpace;

        public v2 NDCofPerspective;

        public v2 NDCofSpherical;

        public v2 PerspectiveImageCoord;

        public v2 SphericalImageCoord;

        public float PerspectiveDistanceToV0;

        public float SphericalDistanceToV0;

        public float PerspectiveDistortion;

        public float SphericalDistortion;

        public Vector2 vp()
        {
            Vector2 v = new Vector2();
            v.x = PerspectiveImageCoord.x;
            v.y = PerspectiveImageCoord.y;
            return v;
        }
        public Vector2 vs()
        {
            Vector2 v = new Vector2();
            v.x = SphericalImageCoord.x;
            v.y = SphericalImageCoord.y;
            return v;
        }
    }

    public struct v3
    {
        public float x;
        public float y;
        public float z;
    }

    public struct v2
    {
        public float x;
        public float y;
    }
}