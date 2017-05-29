using Microsoft.AspNet.SignalR;
using Microsoft.AspNet.SignalR.Hubs;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Emokit.API.Server.Interfaces
{
    public interface IEmokitService
    {
        string EmokitStatus();
        bool EmokitInit();
        bool EmokitStart();
        bool EmokitStop();
    }
}
