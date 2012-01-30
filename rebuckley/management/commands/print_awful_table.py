import locale

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.models import Sum


from rebuckley.models import Expenditure

class Command(BaseCommand):
    help = "Populate the expenditure table from the independent expenditure csv file. Use a 2-digit cycle"
    requires_model_validation = False




    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    key_list = ("C00490045", "C00501098", "C00495861", "C00503417", "C00502971", "C00502377", "C00499525", "C00499335", "C00505180", "C00505719", "C00506972", "C00507525", "C00498261", "C00488767", "C00497941", "C00497958", "C00497966", "C00499095", "C00499731", "C00502641", "C00508002", "C00507921", "C00508317", "C00505081", "C00508721", "C00498097")

    #key_list = ["C00490045"]

    item_list = []
    running_total = 0
    for i in (key_list):
        total_found = Expenditure.objects.filter(raw_committee_id=i, superceded_by_amendment=False).aggregate(total_spent=Sum('expenditure_amount'))
        total = total_found['total_spent']
        if (total == None):
            total = 0
        running_total += total
        formatted_num = locale.format('%d', total, True)
        print formatted_num
        item_list.append(formatted_num)
        print "%s: %s" % ("NAME", formatted_num)

    total_formatted = locale.format('%d', running_total, True)
    print running_total
    item_list.append(total_formatted)

    local_file = open("newchart.html", 'w')

    whole_file = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html><head>
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
      <title></title>
      <style type="text/css">
    /* ------------------
      styling for the tables
            ------------------      */


      body
      {
           line-height: 1.6em;
           font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
           font-size: 11px;
           color: #58595B;
           background-color: #eeefeb;
      }
      a:link { outline: none; color: #457b80; }
      a:visited { outline: none; color: #457b80; }
      a:hover { outline: none; color: #124a50; }
      a:active { outline: none; color: #457b80; }

      #hor-minimalist-a
      {
           font-family: "Lucida Sans Unicode", "Lucida Grande", Sans-Serif;
           font-size: 11px;
           background: #fff;
           margin: 0 0 100px 0;
           width: 570px;
           border-collapse: collapse;
           text-align: left;
      }
      #hor-minimalist-a th
      {
           font-size: 12px;
           font-weight: bold;
           color: #58595B;
           padding: 11px 8px;
           border-bottom: 2px solid #457b80;
           vertical-align: bottom;
      }
      #hor-minimalist-a td
      {
           color: #58595B;
           padding: 9px 8px 0px 8px;
      }

      thead { background-color: #eeefeb; }
      tr.odd { background-color: #eeefeb; }
      tr.even { background-color: #dfe0da; }

      #hor-minimalist-a td:first-child a { display: block; margin-bottom: 8px; }

      #hor-minimalist-a tr td:first-child:hover div.moreinfo { display: block; }
      div.moreinfo {
           background-color: #eeefeb;
           border: 1px solid #457b80;
           display: none;
           margin: -4px 0 0 5px;
           padding: 5px 20px;
           position: absolute;
           box-shadow: 0 0 5px #999;
           -webkit-border-radius: 2px;
                    -moz-border-radius: 2px;
                           border-radius: 2px;
      }
      div.moreinfo ul, div.moreinfo ol { padding-left: 15px; }

      </style>
    </head>

    <body>
      <center>
        <h3>Presidential Super PACs</h3>
      </center>

      <table id="hor-minimalist-a">
        <thead>
          <tr>
            <th scope="col">Super PAC name</th>

            <th scope="col">Supports/Opposes</th>

            <th scope="col">Connection to Candidate</th>

            <th scope="col">Contributions Reported to FEC</th>

            <th scope="col">Independent Expenditures</th>
          </tr>
        </thead>

        <tbody>
          <tr class="odd">
            <td>
              Restore Our Future

              <div class="moreinfo">
                <p>Restore Our Future:</p>

                <ul>
                  <li><a href="http://www.restoreourfuture.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00490045" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/restore-our-future-look-super-pac-helped-romney-and-infuriated-g/" target="_blank">Profile</a></li>
                </ul>
              </div>
            </td>

            <td>supports Romney</td>

            <td><a href="http://www.clarkhill.com/templateBio.aspx?pageID=75&amp;lawyerid=321" target="_blank">Charles R. Spies</a>, <a href="http://www.washingtonpost.com/politics/romney-backers-launch-super-pac/2011/06/22/AGTkGchH_story.html" target="_blank">Carl Forti, Larry McCarthy</a></td>

            <td>$12,231,700</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Our Destiny PAC

              <div class="moreinfo">
                <p>Our Destiny PAC:</p>

                <ul>
                  <li><a href="http://ourdestinypac.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00501098" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Huntsman</td>

            <td><a href="http://www.politico.com/news/stories/0811/62292.html" target="_blank">Fred Davis,</a> <a href="http://www.nytimes.com/2011/11/15/us/politics/major-ad-blitz-planned-for-huntsman-in-new-hampshire.html?_r=1" target="_blank">Jon Huntsman Sr.</a></td>

            <td>None</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Priorities USA Action

              <div class="moreinfo">
                <p>Priorities USA Action:</p>

                <ul>
                  <li><a href="http://www.prioritiesusaaction.org/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/cancomsrs/?_12+C00495861" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/super-pac-profile-obama-supported-priorities-usa-action/">Profile</a></li>
                </ul>
              </div>
            </td>

            <td>supports Obama</td>

            <td><a href="http://abcnews.go.com/blogs/politics/2011/04/former-white-house-aides-starting-non-disclosing-independent-group-like-the-kind-president-obama-cal/" target="_blank">Bill Burton, Sean Sweeney</a></td>

            <td>$3,161,535</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Red, White and Blue Fund

              <div class="moreinfo">
                <p>Red, White and Blue Fund:</p>

                <ul>
                  <li><a href="http://rwbfund.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/cancomsrs/?_12+C00503417" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/red-white-and-blue-pac-supports-santorum/">Profile</a></li>
              </ul></div>
            </td>

            <td>supports Santorum</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Indyamericans.com

              <div class="moreinfo">
                <p>Indyamericans.com:</p>

                <ul>
                  <li><a href="http://indyamericans.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/cancomsrs/?_12+C00502971" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>opposes Perry</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Texans for America's Future

              <div class="moreinfo">
                <p>Texans for America's Future:</p>

                <ul>
                  <li><a href="http://texansforabetteramerica.org/" target="_blank">PAC website</a></li>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00502377" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>opposes Perry</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Keep Conservatives United

              <div class="moreinfo">
                <p>Keep Conservatives United:</p>

                <ul>
                  <li><a href="http://www.keepconservativesunited.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/cancomsrs/?_12+C00499525" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Bachmann</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Revolution PAC

              <div class="moreinfo">
                <p>Revolution PAC:</p>

                <ul>
                  <li><a href="http://www.revolutionpac.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00499335" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/revolution-pac-super-pac-launches-NH-ad-campaign-ron-paul/">Profile</a></li>
                </ul>
              </div>
            </td>

            <td>supports Paul</td>

            <td><a href="http://www.revolutionpac.com/advisory-board/" target="_blank">Joe Becker, Paul Langford</a></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Texas Aggies for Perry 2012

              <div class="moreinfo">
                <p>Texas Aggies for Perry 2012:</p>

                <ul>
                  <li><a href="http://www.texasaggiesforperry.org/" target="_blank">PAC website</a></li>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00505180" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Perry</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Solutions 2012

              <div class="moreinfo">
                <p>Solutions 2012:</p>

                <ul>
                  <li><a href="http://solutions2012.org/" target="_blank">PAC website</a></li>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00505719" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Gingrich</td>

            <td><a href="http://www.rollcall.com/issues/57_75/Close-Super-PAC-Ties-Draw-Ire-211067-1.html?zkMobileView=true" target="_blank">Charlie Smith</a></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Republican Truth Squad

              <div class="moreinfo">
                <p>Republican Truth Squad:</p>

                <ul>
                  <li><a href="http://republicantruthsquad.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00506972" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>opposes Romney</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Winning Our Future

              <div class="moreinfo">
                <p>Winning Our Future:</p>

                <ul>
                  <li><a href="http://www.winningourfuture.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00507525" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/gingrich-super-pac-raises-over-2-million-looks-donors-gingrich-p/">Profile</a></li>
                </ul>
              </div>
            </td>

            <td>supports Gingrich</td>

            <td><a href="http://thecaucus.blogs.nytimes.com/2011/12/13/former-gingrich-aide-forms-fund-raising-group/" target="_blank">Becky Burkett</a>, <a href="http://www.washingtonpost.com/blogs/election-2012/post/gingrich-aide-rick-tyler-joins-super-pac-to-boost-campaign/2011/12/20/gIQAeiT06O_blog.html">Rick Tyler</a>, <a href="http://www.nytimes.com/2012/01/10/us/politics/sheldon-adelson-a-billionaire-gives-gingrich-a-big-lift.html?pagewanted=all">Sheldon Adelson</a></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Americans for Rick Perry

              <div class="moreinfo">
                <p>Americans for Rick Perry:</p>

                <ul>
                  <li><a href="https://www.americansforrickperry.com/AfRP_National/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00498261" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Perry</td>

            <td><a href="http://blog.chron.com/txpotomac/2011/07/texas-businessman-nate-crain-named-finance-chairman-of-americans-for-rick-perry/" target="_blank">Nate Crain</a></td>

            <td>$193,000</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Citizens for Working America PAC

              <div class="moreinfo">
                <p>Citizens for Working America PAC:</p>

                <ul>
                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00488767" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/super-pac-profile-citizens-working-america-tries-fly-under-radar/">Profile</a></li>
              </ul></div>
            </td>

            <td>supports Romney</td>

            <td></td>

            <td>$858</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Jobs for Florida*

              <div class="moreinfo">
                <p>Jobs for Florida:</p>

                <ul>
                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00497941" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Perry</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Jobs for Iowa*

              <div class="moreinfo">
                <p>Jobs for Iowa:</p>

                <ul>
                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00497958" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Perry</td>

            <td></td>

            <td>$136,000</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Jobs for South Carolina*

              <div class="moreinfo">
                <p>Jobs for South Carolina:</p>

                <ul>
                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00497966" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Perry</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Veterans for Rick Perry*

              <div class="moreinfo">
                <p>Veterans for Rick Perry:</p>

                <ul>
                  <li><a href="http://veteransforrickperry.org/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00499095" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Perry</td>

            <td><a href="http://www.huffingtonpost.com/2011/08/13/rick-perry-super-pacs-rai_n_925943.html" target="_blank">Dan Shelley</a></td>

            <td>$16,625</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Make Us Great Again

              <div class="moreinfo">
                <p>Make Us Great Again:</p>

                <ul>
                  <li><a href="http://makeusgreatagain.com/" target="_blank">PAC website</a></li>

                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00499731" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/make-us-great-again-pro-perry-super-pac-ties-former-staff-major-/" target="_blank">Profile</a></li>
                </ul>
              </div>
            </td>

            <td>supports Perry</td>

            <td><a href="http://www.texastribune.org/texas-lobbying/mike-toomey/about/" target="_blank">Mike Toomey</a>, <a href="http://reporting.sunlightfoundation.com/2012/make-us-great-again-pro-perry-super-pac-ties-former-staff-major-/">Brint Ryan</a></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Freedom and Liberty PAC

              <div class="moreinfo">
                <p>Freedom and Liberty PAC:</p>

                <ul>
                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00502641" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Johnson</td>

            <td><a href="http://www.politico.com/politicoinfluence/0911/politicoinfluence108.html" target="_blank">Kelly Casaday</a></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Endorse Liberty Inc

              <div class="moreinfo">
                <p>Endorse Liberty Inc:</p>

                <ul>
                  <li><a href="http://www.endorseliberty.com/home.php" target="_blank">PAC website</a></li>
                  <li><a href="http://query.nictusa.com/cgi-bin/cancomsrs/?_12+C00508002" target="_blank">Registration</a></li>
                  <li><a href="http://reporting.sunlightfoundation.com/2012/super-pac-profile-founders-endorse-liberty-line-their-pockets-wh/" target="_blank">Profile</a></li>
                </ul>
              </div>
            </td>

            <td>supports Paul</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Ron Paul Volunteers PAC

              <div class="moreinfo">
                <p>Ron Paul Volunteers PAC:</p>

                <ul>
                  <li><a href="http://query.nictusa.com/cgi-bin/cancomsrs/?_12+C00507921" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/ron-paul-volunteers/" target="_blank">Profile</a></li>
                </ul>
              </div>
            </td>

            <td>supports Paul</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="odd">
            <td>
              Leaders for Families Super PAC

              <div class="moreinfo">
                <p>Leaders for Families PAC:</p>

                <ul>
                  <li><a href="http://query.nictusa.com/cgi-bin/fecimg/?C00508317" target="_blank">Registration</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/valuable-family-super-pac-behind-santorums-iowa-surge/" target="_blank">Profile</a></li>

                  <li><a href="http://reporting.sunlightfoundation.com/2012/valuable-family-super-pac-behind-santorums-iowa-surge/">Profile</a></li>
              </ul></div>
            </td>

            <td>supports Santorum</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>

          <tr class="even">
            <td>
              Strong America Now

              <div class="moreinfo">
                <p>Strong America Now:</p>

                <ul>
                  <li><a href="http://strongamericanow.org/" target="_blank">PAC website</a></li>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00505081" target="_blank">Registration</a></li>
                </ul>
              </div>
            </td>

            <td>supports Gingrich</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>
           <tr class="odd">
            <td>
              Santa Rita SuperPAC

              <div class="moreinfo">
                <p>Santa Rita SuperPAC:</p>

                <ul>

                  <li><a href="http://images.nictusa.com/cgi-bin/fecimg/?C00508721" target="_blank">Registration</a></li>
                    <li><a href="http://santaritasuperpac.org/" target="_blank">PAC website</a></li>


                  <li><a href="http://reporting.sunlightfoundation.com/2012/super-pac-profile-ron-paul-pac-has-corporate-address/" target="_blank">Profile</a></li>
              </ul></div>
            </td>

            <td>supports Paul</td>

            <td></td>

            <td>$0</td>

            <td>$%s</td>
          </tr>
      
          <tr class="even">
                  <td>
                    Americans for a Better Tomorrow, Tomorrow

                    <div class="moreinfo">
                      <p>Americans for a Better Tomorrow, Tomorrow:</p>

                      <ul>

                        <li><a href=" http://images.nictusa.com/pdf/383/11030620383/11030620383.pdf#navpanes=0" target="_blank">Registration</a></li>

                          <li><a href=" http://www.colbertsuperpac.com/" target="_blank">PAC website</a></li>


                        <li><a href=" http://reporting.sunlightfoundation.com/2012/super-pac-profile-stephen-colbert-jon-stewart-not-coordinating/" target="_blank">Profile</a></li>
                    </ul></div>
                  </td>

                  <td>supports Cain, opposes Romney, Gingrich</td>

                  <td></td>

                  <td>$0</td>

                  <td>$%s</td>
                </tr>

          <tr class="odd"><td colspan=5 style="text-align:right; padding:5px; padding-right: 10px;" ><span style="font-size:18px;"><b>Total spent so far:&nbsp;$%s</b></span></td></tr>
        </tbody>
      </table>
  
  
      * These super PACs have filed termination reports with the FEC.
    <p><em>Updated 9 a.m. Jan. 27 </em></p>

  


    </body></html>
    """ % tuple(item_list)

    local_file.write(whole_file)

    #local_file.close()
