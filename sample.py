#pipenv run python sample.py
import logging
import pandas as pd
from tabulate import tabulate 

from trumania.core import circus, operations
from trumania.core.random_generators import SequencialGenerator, FakerGenerator, NumpyRandomGenerator, ConstantDependentGenerator, ConstantGenerator
import trumania.core.util_functions as util_functions
from trumania.components.time_patterns.profilers import DefaultDailyTimerGenerator, WorkHoursTimerGenerator, CyclicTimerGenerator

from trumania.core.util_functions import make_random_bipartite_data, setup_logging
from trumania.core.operations import FieldLogger, Apply
from trumania.core.clock import CyclicTimerGenerator, CyclicTimerProfile

num_user = 300
num_sites = 10
hrs = "48h"
#2 days

setup_logging()
start_date = pd.Timestamp("09 Aug 2020 00:00:00")

example1 = circus.Circus(
    name="example1",
    master_seed=123456,
    start=start_date,
    step_duration=pd.Timedelta("1h"))

person = example1.create_population(
    name="person", size=1000,
    ids_gen=SequencialGenerator(prefix=""))

person.create_attribute(
    "NAME",
    init_gen=FakerGenerator(method="name",
                            seed=next(example1.seeder)))
							
activity =(100, 100, 100, 100, 54, 54, 54, 26, 20, 22)
normed_activity = [float(i)/sum(activity) for i in activity]
"""
sites = SequencialGenerator(prefix="").generate(num_sites)										
random_site_gen = NumpyRandomGenerator(method="choice", a=sites,
                                        seed=next(example1.seeder),
                                        p=normed_activity)

allowed_sites = person.create_relationship(name="sites")

# Add HOME sites
allowed_sites.add_relations(from_ids=person.ids,
                            to_ids=random_site_gen.generate(person.size),
                            weights=0.4)

# Add WORK sites
allowed_sites.add_relations(from_ids=person.ids,
                            to_ids=random_site_gen.generate(person.size),
                            weights=0.3)

# Add OTHER sites
for i in range(3):
    allowed_sites \
        .add_relations(from_ids=person.ids,
                        to_ids=random_site_gen.generate(person.size),
                        weights=0.1)
"""

#activity levels
#work hours
story_timer_gen = WorkHoursTimerGenerator(
    clock=example1.clock, 
    seed=next(example1.seeder), start_hour=5, end_hour=20)

#default
story_timer_gen = DefaultDailyTimerGenerator(
    clock=example1.clock, 
    seed=next(example1.seeder))

#defined
#http://realimpactanalytics.github.io/trumania/_modules/trumania/components/time_patterns/profilers.html
start_hour = 9
end_hour = 17
# if start_hour = 0, before_work is empty
before_work = [0] * start_hour
during_work = [1.] * (end_hour - start_hour + 1)
# if end_hour = 23, after_work is empty
after_work = [0] * (23 - end_hour)

# the sum of before_work, during_work and after_work is always 24
week_day_profile = before_work + during_work + after_work
weekend_day_profile = [0] * 24

week_profile = week_day_profile * 5 + weekend_day_profile * 2
week_profile = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1, 1.0, 1.0, 0, 0, 0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

story_timer_gen = CyclicTimerGenerator(
    clock=example1.clock, 
    seed=next(example1.seeder), config=CyclicTimerProfile(
                                    profile=week_profile,
                                    profile_time_steps="1h",
                                    start_date=start_date))

low_activity = story_timer_gen.activity(n=10, per=pd.Timedelta("1 day"))
med_activity = story_timer_gen.activity(n=15, per=pd.Timedelta("1 day"))
high_activity = story_timer_gen.activity(n=20, per=pd.Timedelta("1 day"))

activity_gen = NumpyRandomGenerator(
    method="choice", 
    a=[low_activity, med_activity, high_activity],
    p=[0, 0, 1],
    seed=next(example1.seeder))


hello_world = example1.create_story(
    name="hello_world",
    initiating_population=person,
    member_id_field="PERSON_ID",

    # after each story, reset the timer to 0, so that it will get
    # executed again at the next clock tick (next hour)
    timer_gen=story_timer_gen,
    activity_gen=activity_gen

)

#3600 seconds
duration_gen = NumpyRandomGenerator(method="exponential", scale=3600,
                                    seed=next(example1.seeder))


hello_world.set_operations(
    person.ops.lookup(
        id_field="PERSON_ID",
        select={"NAME": "NAME"}
    ),

    duration_gen.ops.generate(named_as="DURATION"),

    ConstantGenerator(value=1).ops.generate(named_as="LOCATION"),

    example1.clock.ops.timestamp(named_as="TIME"),

    FieldLogger(log_id="dummy")
)

example1.run(
    duration=pd.Timedelta("96h"),
    log_output_folder="output/example1",
    delete_existing_logs=True
)

df = pd.read_csv("output/example1/dummy.csv")
print(df)

"""
with open("output/example1/dummy.csv") as f:
    print("Logged {} lines".format(len(f.readlines()) - 1))



# import pandas as pd
# import numpy as np
# sample = pd.read_csv('output/example1/hello.csv', delimiter = ',')
# sample_time = pd.to_datetime(sample.TIME)
# time_profile = (
#     sample[["SITE", "TIME"]]
#     .groupby(by=sample_time.dt.hour)["SITE"]
#     .count()
# )
# time_profile.plot()

"""