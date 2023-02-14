using System.Collections.Generic;
using System.Xml;
using System.Xml.Serialization;
using System.IO;

namespace XMLSerializer
{
    [XmlRoot("ProjectionEvaluation")]
    public class ProjEvaluation
    {
        [XmlElement("VerticalFoV")]
        public float verticalFoV;

        [XmlElement("ImageWidth")]
        public float imgWidth;

        [XmlElement("ImageHeight")]
        public float imgHeight;

        [XmlElement("Near")]
        public float n;

        [XmlElement("Far")]
        public float f;
        
        [XmlElement("MaximalDistortionByPerspective")]
        public float maxDP;

        [XmlElement("MeanDistortionByPerspective")]
        public float meanDP;
        
        [XmlElement("MaximalDistortionBySpherical")]
        public float maxDS;

        [XmlElement("MeanDistortionBySpherical")]
        public float meanDS;

        [XmlElement("NumberOfVertices")]
        public int VCount;

        [XmlArray("Vertices")]
        [XmlArrayItem("Vertex")]
        public List<Vertex> Vertices = new List<Vertex>();

        public void Save(string path)
        {
            var serializer = new XmlSerializer(typeof(ProjEvaluation));
            using (var stream = new FileStream(path, FileMode.Create))
            {
                serializer.Serialize(stream, this);
            }
        }
        public static ProjEvaluation Load(string path)
        {
            var serializer = new XmlSerializer(typeof(ProjEvaluation));
            using (var stream = new FileStream(path, FileMode.Open))
            {
                return serializer.Deserialize(stream) as ProjEvaluation;
            }
        }
    }
}
