using Emokit.API.Server.Hubs;
using Emokit.API.Server.Interfaces;
using Microsoft.AspNet.SignalR;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace Emokit.API.Server.Services
{
    public class EmokitService : IEmokitService
    {
        #region Initialize
        public IHubContext emokitContext { get; set; }
        private static bool hasInitialized { get; set; }
        private static bool hasStarted { get; set; }
        private static bool hasStopped { get; set; }
        private static string status { get; set; }
        private static string dynamicStatus { get; set; }
        #endregion

        public EmokitService()
        {
            emokitContext = GlobalHost.ConnectionManager.GetHubContext<EmokitHub>();
            status = "Emokit Service initialized";
        }

        public bool EmokitInit()
        {
            if (!hasInitialized)
            {
                hasInitialized = true;
                hasStarted = false;
                hasStopped = false;
                emokitContext.Clients.All.OnProducerChanged("init");
                dynamicStatus = " and Emokit initialized";
            }
            return hasInitialized;
        }

        public bool EmokitStart()
        {
            if (hasInitialized & !hasStarted)
            {
                hasStarted = true;
                emokitContext.Clients.All.OnProducerChanged("start");
                dynamicStatus = " and Emokit started";
            }
            return hasStarted;
        }

        public bool EmokitStop()
        {
            hasInitialized = false;
            hasStarted = false;
            hasStopped = true;
            emokitContext.Clients.All.OnProducerChanged("stop");
            dynamicStatus = " and Emokit stopped";
            return hasStopped;
        }

        public string EmokitStatus()
        {
            return status + dynamicStatus;
        }
    }
}