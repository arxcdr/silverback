"""
Status Page Module
"""

# Standard Library
import os
import json
from datetime import datetime
from datetime import timedelta

# Third Party Library
from dateutil.parser import parse
from django.utils import timezone
from pyumetric import Datetime_Utils
from pyumetric import NewRelic_Provider
from django.forms.fields import DateTimeField
from dateutil.relativedelta import relativedelta
from django.utils.translation import gettext as _

# Local Library
from app.modules.entity.option_entity import OptionEntity
from app.modules.entity.metric_entity import MetricEntity
from app.modules.entity.incident_entity import IncidentEntity
from app.modules.entity.component_entity import ComponentEntity
from app.modules.entity.component_group_entity import ComponentGroupEntity
from app.modules.entity.incident_update_entity import IncidentUpdateEntity
from app.modules.entity.incident_update_component_entity import IncidentUpdateComponentEntity


class StatusPage():

    __option_entity = None
    __incident_entity = None
    __incident_update_entity = None
    __incident_update_component_entity = None
    __component_group_entity = None
    __component_entity = None
    __metric_entity = None

    def __init__(self):
        self.__option_entity = OptionEntity()
        self.__incident_entity = IncidentEntity()
        self.__incident_update_entity = IncidentUpdateEntity()
        self.__incident_update_component_entity = IncidentUpdateComponentEntity()
        self.__component_group_entity = ComponentGroupEntity()
        self.__component_entity = ComponentEntity()
        self.__metric_entity = MetricEntity()

    def get_system_status(self):
        # Get Open Incidents
        # if it has no resolved update
        # Check the last incident updates
        # Check it has any component is affected
        return "operational"

    def get_about_site(self):
        option = self.__option_entity.get_one_by_key("builder_about")
        return option.value if option else ""

    def get_logo_url(self):
        option = self.__option_entity.get_one_by_key("builder_logo_url")
        return option.value if option else ""

    def get_favicon_url(self):
        option = self.__option_entity.get_one_by_key("builder_favicon_url")
        return option.value if option else ""

    def get_incident_by_uri(self, uri):
        incident = self.__incident_entity.get_one_by_uri(uri)
        app_name = self.__option_entity.get_one_by_key("app_name")

        if incident:
            incident_data = {
                "headline": incident.name,
                "headline_class": "text-danger",
                "status": incident.status,
                "sub_headline": _("Incident Report for %s") % (app_name.value),
                "affected_components": [],
                "updates": []
            }

            updates = self.__incident_update_entity.get_all(incident.id)

            for update in updates:
                incident_data["updates"].append({
                    "type": update.status.title(),
                    "body": update.message,
                    "date": "%(date)s %(tz)s" % {
                        "date": update.datetime.strftime("%B %d, %H:%M"),
                        "tz": os.getenv("APP_TIMEZONE", "UTC")
                    }
                })

                components = self.__incident_update_component_entity.get_all(update.id)

                for component in components:
                    if component.component.name not in incident_data["affected_components"]:
                        incident_data["affected_components"].append(component.component.name)

            incident_data["affected_components"] = ", ".join(incident_data["affected_components"])

            return incident_data

        return False

    def get_incidents_for_period(self, period):

        today = timezone.now()
        datem = datetime(today.year, today.month, 1)

        from_date = datem - relativedelta(months=+(period - 1) * 3)
        to_date = datem - relativedelta(months=+(period * 3))

        period = "%(from)s - %(to)s" % {
            "from": from_date.strftime("%B %Y"),
            "to": (to_date + relativedelta(months=+1)).strftime("%B %Y")
        }

        from_date = datetime(from_date.year, from_date.month, 1)
        to_date = datetime(to_date.year, to_date.month, 1)

        incidents = []
        while from_date > to_date:
            current_incidents = []

            incidents_list = self.__incident_entity.get_incident_on_month(DateTimeField().clean(from_date))

            for incident in incidents_list:
                current_incidents.append({
                    "uri": incident.uri,
                    "subject": incident.name,
                    "class": "text-danger",
                    "status": incident.status,
                    "final_update": _("This incident has been resolved.") if incident.status == "closed" else _("This incident is still open."),
                    "period": self.__get_incident_period(incident)
                })

            current_date = from_date.strftime("%B %Y")
            incidents.append({
                "date": current_date,
                "incidents": current_incidents
            })
            from_date -= relativedelta(months=+1)

        return {
            "period": period,
            "incidents": incidents
        }

    def __get_incident_period(self, incident):
        updates = self.__get_incident_updates(incident.id)
        if len(updates):
            return "%(from)s %(tz)s - %(to)s" % {
                "from": incident.datetime.strftime("%B %d, %H:%M"),
                "tz": os.getenv("APP_TIMEZONE", "UTC"),
                "to": updates[len(updates)-1]["date"]
            }
        return "%(from)s %(tz)s" % {
            "from": incident.datetime.strftime("%B %d, %H:%M"),
            "tz": os.getenv("APP_TIMEZONE", "UTC")
        }

    def get_past_incidents(self, days=7):
        i = 0
        past_incidents = []
        while days > i:
            date = (datetime.now() - timedelta(days=i))
            incidents_result = []
            incidents = self.__incident_entity.get_incident_from_days(i)
            for incident in incidents:
                incidents_result.append({
                    "uri": incident.uri,
                    "subject": incident.name,
                    "class": "text-danger",
                    "status": incident.status,
                    "updates": self.__get_incident_updates(incident.id)
                })

            past_incidents.append({
                "date": date.strftime("%B %d, %Y"),
                "incidents": incidents_result
            })
            i += 1
        return past_incidents

    def __get_incident_updates(self, incident_id):
        updates_result = []
        updates = self.__incident_update_entity.get_all(incident_id)
        for update in updates:
            updates_result.append({
                "type": update.status.title(),
                "date": "%(date)s %(tz)s" % {
                    "date": update.datetime.strftime("%B %d, %H:%M"),
                    "tz": os.getenv("APP_TIMEZONE", "UTC")
                },
                "body": update.message
            })
        return updates_result

    def get_system_metrics(self):
        metrics = []
        option = self.__option_entity.get_one_by_key("builder_metrics")
        if option:
            items = json.loads(option.value)
            for item in items:
                if "m-" in item:
                    item = int(item.replace("m-", ""))
                    if item:
                        metric = self.__metric_entity.get_one_by_id(item)
                        if metric:
                            metrics.append({
                                "id": "metric_container_%d" % (metric.id),
                                "title": metric.title,
                                "xtitle": metric.x_axis,
                                "ytitle": metric.y_axis,
                                "day_data": self.__get_metrics(metric, -1),
                                "week_data": self.__get_metrics(metric, -7),
                                "month_data": self.__get_metrics(metric, -30)
                            })
        return metrics

    def __get_metrics(self, metric, period):
        metric_values = []
        option = self.__option_entity.get_one_by_key("newrelic_api_key")

        if not option:
            raise Exception("Unable to find option with key newrelic_api_key")

        new_relic_client = NewRelic_Provider(option.value)

        if metric.source == "newrelic":
            data = json.loads(metric.data)

            if data["metric"] == "response_time":
                response = new_relic_client.get_metric(
                    data["application"],
                    ["WebTransaction"],
                    ["average_response_time"],
                    Datetime_Utils("UTC", period).iso(),
                    Datetime_Utils("UTC").iso(),
                    False
                )
                if len(response) > 0:
                    response = json.loads(response)

                    if "metric_data" not in response:
                        raise Exception(_("Error: Unable to find metric_data on NewRelic response!"))

                    if "WebTransaction" not in response["metric_data"]["metrics_found"]:
                        raise Exception(_("Error: Unable to find metric WebTransaction on NewRelic response!"))

                    if "metrics" not in response["metric_data"] or len(response["metric_data"]["metrics"]) < 1:
                        raise Exception(_("Error: Unable to find metric metrics on NewRelic response!"))

                    for item in response["metric_data"]["metrics"][0]["timeslices"]:
                        metric_values.append({
                            "timestamp": datetime.timestamp(parse(item["from"])),
                            "value": item["values"]["average_response_time"]
                        })
            elif data["metric"] == "apdex":
                raise Exception(_("Error: NewRelic apdex metric not implemented yet!"))

            elif data["metric"] == "error_rate":
                raise Exception(_("Error: NewRelic error_rate metric not implemented yet!"))

            elif data["metric"] == "throughput":
                raise Exception(_("Error: NewRelic throughput metric not implemented yet!"))

            elif data["metric"] == "errors":
                raise Exception(_("Error: NewRelic errors metric not implemented yet!"))

            elif data["metric"] == "real_user_response_time":
                raise Exception(_("Error: NewRelic real_user_response_time metric not implemented yet!"))

            elif data["metric"] == "real_user_apdex":
                raise Exception(_("Error: NewRelic real_user_apdex metric not implemented yet!"))

        return metric_values

    def get_services(self):
        services = []
        option = self.__option_entity.get_one_by_key("builder_components")
        if option:
            items = json.loads(option.value)
            for item in items:
                if "c-" in item:
                    component = self.__component_entity.get_one_by_id(item.replace("c-", ""))
                    if component:
                        services.append({
                            "name": component.name,
                            "description": component.description,
                            "current_status": self.get_status(component.id, "component"),
                            "current_status_class": "bg-green",
                            "uptime_chart": self.get_uptime_chart(component.id, "component"),
                            "sub_services": []
                        })
                elif "g-" in item:
                    group = self.__component_group_entity.get_one_by_id(item.replace("g-", ""))
                    services.append({
                        "name": group.name,
                        "description": group.description,
                        "current_status": self.get_status(group.id, "group"),
                        "current_status_class": "bg-green",
                        "uptime_chart": self.get_uptime_chart(group.id, "group"),
                        "sub_services": self.get_sub_services(group.id)
                    })

        return services

    def get_sub_services(self, group_id):
        services = []
        items = self.__component_entity.get_all_components_by_group(group_id)
        for item in items:
            services.append({
                "name": item.name,
                "description": item.description,
                "current_status": self.get_status(item.id, "component"),
                "current_status_class": "bg-green",
                "uptime_chart": self.get_uptime_chart(item.id, "component"),
                "sub_services": []
            })
        return services

    def get_status(self, id, type):
        # Get Open Incidents
        # if it has no resolved update
        # Check the last incident updates
        # Check if the component is affected
        if type == "component":
            return "Operational"

        # Get Group Components
        # Get Open Incidents
        # if it has no resolved update
        # Check the last incident updates
        # Check if one of the group components is affected
        elif type == "group":
            return "Operational"

    def __get_affectd_components(self):
        # Get Open Incidents
        # if it has no resolved update
        # Check the last incident updates
        # Create a list of affected components
        return {}

    def get_uptime_chart(self, id, type, period=90):
        return []
