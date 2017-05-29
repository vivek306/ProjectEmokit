using Emokit.API.Server.Interfaces;
using Emokit.API.Server.Services;
using Microsoft.AspNet.SignalR;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace Emokit.API.Server.Hubs
{
    public class EmokitHub : Hub
    {
        public IEmokitService emokitService { get; set; }

        public EmokitHub()
        {
            emokitService = new EmokitService();
        }

        public bool Init()
        {
            return emokitService.EmokitInit();
        }

        public bool Start()
        {
            return emokitService.EmokitStart();
        }

        public bool Stop()
        {
            return emokitService.EmokitStop();
        }
    }
}