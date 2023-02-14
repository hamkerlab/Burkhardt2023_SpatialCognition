/**
\mainpage A simple-to-use networkinterface that uses ProtoBuf and TCP/IP, it connect Unity (C#/Windows) and ANNarchy (C++/Linux)

 @section General idea
 The receiving and sending are separated in two extra threads.
 The function controller is running on an own background thread too.
 It accepts incomming new clients (at the moment, only one connected client is allowed).
 The send function puts the data in a MsgObject and in a buffer.
 The data is then sent in the background.
      
 If data is received, the background thread for receiving puts the data into a buffer.
 The user gets the data by calling the receive function.
 It is important to call the stop function to abort all background threads!

 @section How to add new Msg-types
 - 1) Create new class and do not forget the Protobuf attributes.
 - 2) Add class to the MsgObject-class in such a way that this class knows how to handle the new datatype.
 - 3) Add the new Message to the Protofile.
    
@section Installation:
 - If you recompile, everything should be copied automatically into the right place.
 - If manually: copy simplenet.dll into the folder: unityVR/assets/plugins 

@brief I/O class to receive data from the virtual reality (VR) into ANNarchy (or C++ in general).

:copyright: Copyright 2013-2023, see AUTHORS.
:license: GPLv3, see LICENSE for details.
**/


using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net.Sockets;
using System.Net;
using System.IO;
using ProtoBuf;
using UnityEngine;

namespace SimpleNetwork
{
    public class SimpleNet
    {
        TcpListener TCPListener;
        TcpClient Client;
        NetworkStream ClientDataStream;

        Queue<MsgObject> SimpleMsgOut = new Queue<MsgObject>();
        Queue<MsgObject> ImagesOut = new Queue<MsgObject>();

        Queue<MsgObject> MsgInbox = new Queue<MsgObject>();

        System.Threading.Thread ConntrolThread;
        System.Threading.Thread ReceiveThread;
        System.Threading.Thread SendThread;

        // Logging
        public bool logSimpleNet { get; private set; }
        private System.IO.StreamWriter file = null;

        /// <summary>
        /// Creates an instance of the SimpleNetwork.
        /// </summary>
        /// <param name="IP">Optional:IP the server listens to. (default 127.0.0.1)</param>
        /// <param name="Port">Optional Port to wait for incoming connections (default 1337)</param>
        public SimpleNet(string IP, int Port, bool logSimpleNet = false)
        {
            this.logSimpleNet = logSimpleNet;
            if (logSimpleNet) file = new System.IO.StreamWriter("log_SimpleNet" + DateTime.Now.ToString("yyyyMMddHHmmssfff") + "_" + Port + ".txt");
            log("Start logging\n");

            TCPListener = new TcpListener(IPAddress.Parse(IP), Port);
            TCPListener.Start();
            ConntrolThread = System.Threading.Thread.CurrentThread;

            //im Hintergrund laufen immer diese Prodzeduren
            ConntrolThread= Run(Controler); //Im Hintergrud läuft immer diese Prozedur
            SendThread = Run(BackgroundDatasendingLoop);
            ReceiveThread = Run(BackroundRecivingLoop);
        }

        /// <summary>
        /// Logs a given string if logging is enabled
        /// </summary>
        /// <param name="s">The string to log</param>
        private void log(string s) {
            if (logSimpleNet) {
                file.WriteLine(s);
                file.Flush();
            }
        }
        
        //mehr bilder zwichen Fehlermeldung wenn nicht alle bilder übermittelt werden können
        //fehler bei überlastung generell TODO

        /// <summary>
        /// Sends a Msg over the network to the client. Function takes care of identification of the Data, and "builds" an
        /// corresponding MsgObject that is enqueued for sending over the network in a background thread.
        /// </summary>
        /// <param name="Object">Any instance of an MsgX-class</param>
        public void Send(object Object)
        {
            if (IsConnected)
            {
                MsgObject MyMsgObject = new MsgObject(Object);

                //Bilder Kommen in eigene Queue
                if (Object.GetType() == typeof(MsgImages))
                {
                    lock (ImagesOut)
                    {
                        ImagesOut.Enqueue(MyMsgObject);
                        while (ImagesOut.Count > 2)//Wir Puffern nur 2 Bilder
                        {
                            ImagesOut.Dequeue();
                        }
                        return;
                    }
                }

                lock (SimpleMsgOut)
                {
                    SimpleMsgOut.Enqueue(MyMsgObject);
                }
            }
        }

        /// <summary>
        /// Takes a MsgObject from the queue of available revived data. Waits if there is no data available!
        /// </summary>
        /// <returns>First MsgObject in Queue</returns>
        public MsgObject Receive()
        {
            while (MsgInbox.Count == 0)
            {
                System.Threading.Thread.Sleep(1); //Pop wartet bis Daten da sind, es ist blockierend!
            }
            
            lock (MsgInbox)
            {
               return MsgInbox.Dequeue();
            }
        }

        /// <summary>
        /// Indicates whether there were messages received.
        /// </summary>
        /// <returns>true if Data available</returns>
        public bool MsgAvailable()
        {
            return MsgInbox.Count != 0;
        }

        /// <summary>
        /// Checks whether there is a client connected.
        /// </summary>
        public bool IsConnected
        {
            get
            {
                return Client != null && Client.Connected;
            }
        }
        
        /// <summary>
        /// Actual sending of data over the wire is managed by this function in the background. It takes the data from the SimpleMsg- and Image-OutBox. SimpleMsg are allways sent first.
        /// </summary>
        private void BackgroundDatasendingLoop()
        {

            log("BackgroundDataSendingLoop"); //DEBUG
            while (true)
            {
                if (die)
                    return;

                while (ClientDataStream == null)
                {
                    log("BackgroundSendingLoop: wait for ClientDataStream is not null"); //DEBUG
                    System.Threading.Thread.Sleep(1000);
                }

                try
                {

                    //Send Simple Data to Client
                    if (IsConnected && SimpleMsgOut.Count > 0)
                    {
                        MsgObject MsgToSend;
                        lock (SimpleMsgOut)
                        {
                            MsgToSend = SimpleMsgOut.Dequeue();
                        }
                        Serializer.SerializeWithLengthPrefix<MsgObject>(ClientDataStream, MsgToSend, PrefixStyle.Fixed32);
                        continue;
                    }

                    //Send Images to Client
                    if (IsConnected && ImagesOut.Count > 0)
                    {
                        MsgObject MsgToSend;
                        lock (ImagesOut)
                        {
                            MsgToSend = ImagesOut.Dequeue();
                        }
                        Serializer.SerializeWithLengthPrefix<MsgObject>(ClientDataStream, MsgToSend, PrefixStyle.Fixed32);
                        continue;
                    }

                    //Nothing to do, release the CPU
                    System.Threading.Thread.Sleep(1);
                    //Console.WriteLine("Tick!");
                }
                catch(Exception e) 
                { 
                    Console.WriteLine(e.Message);
                    log("Catched Exception!");
                    log(e.ToString()); // catch protobuf exception
                }
            }
        }

        /// <summary>
        /// Actual receiving of data over the wire is managed by this function in the background. It fills the MsgInbox-Queue.
        /// </summary>
        private void BackroundRecivingLoop()
        {

            log("BackgroundRecievingLoop"); //DEBUG
            while (true)
            {
                if (die)
                    return;

                while (ClientDataStream == null)
                {
                    log("BackgroundRecievingLoop: wait for ClientDataStream is not null"); //DEBUG
                    System.Threading.Thread.Sleep(1000);
                }

                try
                {
                    //Progress Data from Client
                    if (IsConnected)
                    {
                        while (ClientDataStream.DataAvailable)
                        {

                            Console.WriteLine("Starte Empfangen!");
                            log("Starte Empfangen!"); //DEBUG
                            MsgObject Buffer;
							Buffer = Serializer.DeserializeWithLengthPrefix<MsgObject>(ClientDataStream, PrefixStyle.Fixed32);
                            //in spez rein das gleich deserialisiert wird TODO
                            Console.WriteLine("Empfangen fertig");
                            log("Empfangen fertig"); //DEBUG
							
                            lock (MsgInbox)
                            {
                                MsgInbox.Enqueue(Buffer);
                            }
                        }
                    }

                    //Nothing to Do, release the CPU
                    System.Threading.Thread.Sleep(1);
                    //Debug.Log("Tick!");
                }
                catch(Exception e)
				{
                    log("Catched Exception!");
                    log(e.ToString()); // catch protobuf exception
				}
            }
        }

        /// <summary>
        /// Handels incoming connections.
        /// </summary>
        private void Controler()
        {
            log("Controllerloop"); //DEBUG
            while (true)
            {
                if (die)
                    return;
                try
                {
                    //log("Controller: wait for incoming connections"); //DEBUG

                    //Take incoming Connections
                    if (TCPListener.Pending())
                    {
                        Console.WriteLine("Verbindungsaufbau");
                        log("Controller: accept incoming connection"); //DEBUG
                        Client = TCPListener.AcceptTcpClient();
                        ClientDataStream = Client.GetStream();
                        Client.ReceiveBufferSize = 4096;//Every Msg should fit Inside at ones, Ram is Cheap ;)
                        Client.NoDelay = true;
                        log("Controller: configured stream"); //DEBUG
                        //in spezifikation TODO
                    }

                    //Nothing to Do, release the CPU
                    System.Threading.Thread.Sleep(10); // 10 ms
                    //Console.WriteLine("Tick!");
                }
                catch (Exception e) 
                {
                    log("Catched Exception in controller!");
                    log(e.ToString()); // catch protobuf exception
                }
            }
        }

        /// <summary>
        /// If set to true, all the background threads should stop :)
        /// </summary>
        volatile bool die = false;

        /// <summary>
        /// Stops all concurrent threads and closes network connections.
        /// Important to call this function when the programm is terminated to stop all background threads!
        /// </summary>
        public void Stop()
        {
            //We had some problems with freezing becouse of the Network not shutting down
            //so we do everything possible to shut everything down!
            die = true;
            ConntrolThread.Abort();
            SendThread.Abort();
            ReceiveThread.Abort();
            TCPListener.Stop();
            if (Client!=null) Client.Close();
            if (ClientDataStream!=null) ClientDataStream.Close();
            if (logSimpleNet) file.Close();
        }

        /// <summary>
        /// utillity to start Parallel Threats
        /// </summary>
        /// <param name="TheDelagate">Delagate to invoke</param>
        /// <returns></returns>
        static System.Threading.Thread Run(System.Threading.ThreadStart TheDelagate)
        {
            System.Threading.Thread thread = new System.Threading.Thread(TheDelagate);
            thread.Start();
            return thread;
        } 
        
    } 
}
