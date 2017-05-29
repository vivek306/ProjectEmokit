using Emokit.API.Server.Interfaces;
using Emokit.API.Server.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Web.Http;

namespace Emokit.API.Server.Controllers
{
    public class EmokitController : ApiController
    {
        public IEmokitService emokitService { get; set; }

        public EmokitController()
        {
            emokitService = new EmokitService();
        }

        // GET api/emokit
        public IEnumerable<string> Get()
        {
            return new string[] { "EMOKIT API SERVER", emokitService.EmokitStatus() };
        }

        // POST api/emokit
        public void Post(string option)
        {
            switch (option)
            {
                case "init":
                    emokitService.EmokitInit();
                    break;
                case "start":
                    emokitService.EmokitStart();
                    break;
                case "stop":
                    emokitService.EmokitStop();
                    break;
                default:
                    break;
            }
        }
    }
}
