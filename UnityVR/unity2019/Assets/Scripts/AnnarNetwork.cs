/**
@brief
  Together with AnnarLayer, AnnarNeuron, AnnarWeightList and AnnarWeight,
  AnnarNetwork, this is the data class for a neuronal network.
 
  The neuronal network is organized into layers, neurons and weights. AnnarNetwork holds the list of neuronal layers (AnnerLayer) and provides access to these. 
  Each layers holds then their neurons (AnnerNeuron) which in turn stores the weights (AnnarWeightList and AnnerWeight). In summary, the Annar* - casses provide a nested data structure to store a neuronal network.
  
:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System.Collections.Generic;
using System;
using ProtoBuf;

// TODO: some Protobuf related code is not needed anymore and is just here to be backwards compatible.. (Serializable, IsRequired)

[Serializable, ProtoContract]
public class AnnarNetwork
{
    /// <summary>
    /// Boolean to define if the whole network or an update is sent; true if update is sent
    /// </summary>
    [ProtoMember(1, IsRequired = true)]
	public bool Update {get;set;} 
	
	/// <summary>
	/// List of neuronal layers
	/// </summary>
	[ProtoMember(2)]
	public List<AnnarLayer> Layers {get;set;}

    /// <summary>
    /// Timestep of ANNarchy at sending timepoint.
    /// </summary>
    [ProtoMember(3, IsRequired = true)]
    public Int64 step { get; set; } 
	

    /// <summary>
    /// This standard constructor is necessary for protobuf
    /// </summary>
    public AnnarNetwork()
    {
    }

    /// <summary>
    /// Constructor
    /// </summary>
    /// <param name="layers">neuronal network data</param>
    /// <param name="update">True if only an update was sent, false if a new whole network was freshly instantiated</param>
	public AnnarNetwork (List<AnnarLayer> layers, bool update)
	{
	    Update = update;
		Layers = layers;
	}
	
	/// <summary>
	/// Creates a predefined AnnarNetwork object as an toy example.
	/// </summary>
	/// <returns>
	/// The simple network.
	/// </returns>
    static public AnnarNetwork GiveSimpleNetwork()
    {
        /* Network structure
         * 
         * V1: 20 x 2 x 2 neurons
         * V2: 10 x 1 x 2 neurons
         * 
         * Connectivity
         * V1-V2: 4 neurons in a block of 2x2 in V1 are each connected to 1 V2 neuron
         * V2->V2: all to all in each depth plane, except itself
         */

        // Create V2
        List<AnnarNeuron> v2Neurons = new List<AnnarNeuron>();
        AnnarLayer layerV2 = new AnnarLayer(10, 1, 2, "Visual Cortex V2", 1, v2Neurons);

        //Create V1
        List<AnnarNeuron> v1Neurons = new List<AnnarNeuron>();
        for (int i = 0; i < 20 * 2; ++i)
        {
            v1Neurons.Add(new AnnarNeuron(0.1, i / 39.0, null)); //depth plane 1
            v1Neurons.Add(new AnnarNeuron(0.2, i / 39.0, null)); //depth plane 2
        }

        AnnarLayer layerV1 = new AnnarLayer(20, 2, 2, "Visual Cortex V1", 0, v1Neurons);



        // add neurons and connectivity in V2
        List<AnnarWeight> connectionsV2V2;
        List<AnnarWeight> connectionsV1V2;
        List<AnnarWeightList> connectionsListV2V2;


        for (int l = 0; l < 2; l++)
        {
            for (int i = 0; i < 10; i++)
            {

                connectionsListV2V2 = new List<AnnarWeightList>();

                //LAT_POS
                connectionsV2V2 = new List<AnnarWeight>();
                for (int j = 0; j < 10; j++)
                    if (i != j)
                        connectionsV2V2.Add(new AnnarWeight(layerV2.getNeuronRank(j, 0, l), 1, 1.0));
                connectionsListV2V2.Add(new AnnarWeightList(3, connectionsV2V2));

                //FF
                connectionsV1V2 = new List<AnnarWeight>();
                connectionsV1V2.Add(new AnnarWeight(layerV1.getNeuronRank(2 * i, 0, l), 0, 0.0));
                connectionsV1V2.Add(new AnnarWeight(layerV1.getNeuronRank(2 * i + 1, 0, l), 0, 0.25));
                connectionsV1V2.Add(new AnnarWeight(layerV1.getNeuronRank(2 * i, 1, l), 0, 0.5));
                connectionsV1V2.Add(new AnnarWeight(layerV1.getNeuronRank(2 * i + 1, 1, l), 0, 0.75));
                connectionsListV2V2.Add(new AnnarWeightList(1, connectionsV1V2));

                v2Neurons.Add(new AnnarNeuron(0.2, 1 - i / 9.0, connectionsListV2V2));
            }
        }




        // Add previously defined connection structure to the network
        List<AnnarLayer> tmp = new List<AnnarLayer>();
        tmp.Add(layerV1);
        tmp.Add(layerV2);
        return new AnnarNetwork(tmp, false);

    }
	
	
	/// <summary>
	/// Return layer with specific ID
	/// </summary>
	/// <returns>
	/// Layer with ID
	/// </returns>
	/// <param name='id'>
	/// ID of the layer.
	/// </param>
	public AnnarLayer getLayer (int id)
	{
		foreach( var layer in Layers )
			if (layer.Id == id)
				return layer;		
		return null;
	}	
	
	/// <summary>
	/// Return layer with specific name
	/// </summary>
	/// <returns>
	/// Layer with name
	/// </returns>
	/// <param name='name'>
	/// Name of the layer.
	/// </param>
	public AnnarLayer getLayer (string name)
	{
		foreach( var layer in Layers )
			if (layer.Name == name)
				return layer;		
		return null;
	}	
	
}
